# -*- coding: utf-8 -*-
"""Kodi video add-on for user-configured, public/legal M3U sources.

The add-on does not host, proxy, bundle, or redistribute video streams.
Users are responsible for checking the rights and local rules for each source.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from typing import Dict, List, Optional

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")
BASE_URL = sys.argv[0]
HANDLE = int(sys.argv[1])
ARGS = urllib.parse.parse_qs(sys.argv[2][1:]) if len(sys.argv) > 2 and sys.argv[2].startswith("?") else {}
DEFAULT_PLAYLIST = "https://iptv-org.github.io/iptv/index.m3u"
MAX_PLAYLIST_BYTES = 25 * 1024 * 1024


def _param(name: str, default: str = "") -> str:
    values = ARGS.get(name)
    return values[0] if values else default


def _plugin_url(**params: str) -> str:
    return BASE_URL + "?" + urllib.parse.urlencode(params)


def _notify(message: str, heading: Optional[str] = None, icon: str = xbmcgui.NOTIFICATION_INFO) -> None:
    xbmcgui.Dialog().notification(heading or ADDON_NAME, message, icon, 5000)


def _cache_paths() -> tuple:
    profile = xbmcvfs.translatePath(ADDON.getAddonInfo("profile"))
    if not os.path.isdir(profile):
        os.makedirs(profile, exist_ok=True)
    return os.path.join(profile, "playlist.m3u"), os.path.join(profile, "playlist.meta")


def _read_cache(cache_seconds: int, cache_file: str, meta_file: str, playlist_url: str) -> Optional[str]:
    if cache_seconds <= 0:
        return None
    try:
        if not (os.path.isfile(cache_file) and os.path.isfile(meta_file)):
            return None
        with open(meta_file, "r", encoding="utf-8") as meta:
            metadata = json.load(meta)
        # A cache is valid only for the exact configured playlist URL.
        if metadata.get("url") != playlist_url:
            return None
        saved_at = float(metadata["saved_at"])
        if time.time() - saved_at > cache_seconds:
            return None
        with open(cache_file, "r", encoding="utf-8-sig", errors="replace") as playlist:
            return playlist.read()
    except (OSError, ValueError):
        return None


def _write_cache(text: str, cache_file: str, meta_file: str, playlist_url: str) -> None:
    try:
        with open(cache_file, "w", encoding="utf-8") as playlist:
            playlist.write(text)
        with open(meta_file, "w", encoding="utf-8") as meta:
            json.dump({"url": playlist_url, "saved_at": time.time()}, meta)
    except OSError as exc:
        xbmc.log("[%s] No se pudo guardar la caché: %s" % (ADDON_ID, exc), xbmc.LOGWARNING)


def fetch_playlist() -> str:
    """Load the configured M3U with a small on-disk cache."""
    url = ADDON.getSetting("playlist_url").strip() or DEFAULT_PLAYLIST
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("La URL de la lista debe comenzar por http:// o https://")

    try:
        cache_seconds = max(0, int(ADDON.getSetting("cache_seconds") or "1800"))
    except ValueError:
        cache_seconds = 1800

    cache_file, meta_file = _cache_paths()
    cached = _read_cache(cache_seconds, cache_file, meta_file, url)
    if cached is not None:
        return cached

    user_agent = ADDON.getSetting("user_agent").strip() or ("Kodi/%s FREE TV/%s" % (xbmc.getInfoLabel("System.BuildVersion"), ADDON_VERSION))
    request = urllib.request.Request(url, headers={"User-Agent": user_agent, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read(MAX_PLAYLIST_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise RuntimeError("El servidor respondió HTTP %s" % exc.code)
    except urllib.error.URLError as exc:
        raise RuntimeError("No se pudo abrir la lista: %s" % exc.reason)
    if len(data) > MAX_PLAYLIST_BYTES:
        raise RuntimeError("La lista supera el límite de seguridad de 25 MB")

    text = data.decode("utf-8-sig", errors="replace")
    if "#EXTM3U" not in text[:2048]:
        raise RuntimeError("La URL no parece devolver una lista M3U válida")
    _write_cache(text, cache_file, meta_file, url)
    return text


def parse_m3u(text: str) -> List[Dict[str, str]]:
    """Parse common EXTINF M3U entries, retaining only HTTP(S) stream URLs."""
    channels: List[Dict[str, str]] = []
    pending: Optional[Dict[str, str]] = None
    pending_group = "Sin categoría"

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#EXTINF:"):
            meta, separator, display_name = line.partition(",")
            attrs: Dict[str, str] = {}
            for match in re.finditer(r"""([\w-]+)\s*=\s*("[^"]*"|'[^']*'|[^\s]+)""", meta):
                attrs[match.group(1).lower()] = match.group(2).strip("\"'")
            name = (display_name.strip() if separator else "") or attrs.get("tvg-name") or "Canal sin nombre"
            pending_group = attrs.get("group-title", "").strip() or "Sin categoría"
            pending = {
                "name": name,
                "group": pending_group,
                "logo": attrs.get("tvg-logo", ""),
                "tvg_id": attrs.get("tvg-id", ""),
            }
        elif line.startswith("#EXTGRP:"):
            pending_group = line.split(":", 1)[1].strip() or "Sin categoría"
            if pending is not None:
                pending["group"] = pending_group
        elif line.startswith("#"):
            continue
        elif pending is not None:
            stream_url = line
            scheme = urllib.parse.urlparse(stream_url).scheme.lower()
            if scheme in ("http", "https"):
                channel = dict(pending)
                channel["url"] = stream_url
                channels.append(channel)
            pending = None
            pending_group = "Sin categoría"

    return channels


def _make_list_item(label: str, plot: str = "") -> xbmcgui.ListItem:
    item = xbmcgui.ListItem(label=label)
    item.setInfo("video", {"title": label, "mediatype": "video", "plot": plot})
    return item


def show_root() -> None:
    xbmcplugin.setContent(HANDLE, "videos")
    items = [
        (_plugin_url(action="categories"), _make_list_item("Categorías", "Explorar los canales por grupo."), True),
        (_plugin_url(action="all"), _make_list_item("Todos los canales", "Mostrar todos los canales de la lista configurada."), True),
        (_plugin_url(action="search"), _make_list_item("Buscar canal", "Buscar por nombre."), True),
        (_plugin_url(action="settings"), _make_list_item("Ajustes", "Cambiar la URL M3U y la caché."), True),
    ]
    xbmcplugin.addDirectoryItems(HANDLE, items, len(items))
    xbmcplugin.endOfDirectory(HANDLE)


def _load_channels() -> List[Dict[str, str]]:
    playlist = fetch_playlist()
    channels = parse_m3u(playlist)
    if not channels:
        raise RuntimeError("La lista se descargó, pero no contiene canales HTTP/HTTPS reconocibles")
    return channels


def show_categories(channels: List[Dict[str, str]]) -> None:
    categories = sorted({channel["group"] for channel in channels}, key=str.casefold)
    items = []
    for category in categories:
        count = sum(1 for channel in channels if channel["group"] == category)
        label = "%s (%d)" % (category, count)
        items.append((_plugin_url(action="group", group=category), _make_list_item(label), True))
    xbmcplugin.setContent(HANDLE, "files")
    xbmcplugin.addDirectoryItems(HANDLE, items, len(items))
    xbmcplugin.endOfDirectory(HANDLE)


def show_channels(channels: List[Dict[str, str]], group: str = "", query: str = "") -> None:
    filtered = channels
    if group:
        filtered = [c for c in filtered if c["group"].casefold() == group.casefold()]
    if query:
        needle = query.casefold()
        filtered = [c for c in filtered if needle in c["name"].casefold() or needle in c["group"].casefold()]

    filtered.sort(key=lambda c: (c["name"].casefold(), c["group"].casefold()))
    items = []
    for channel in filtered:
        item = _make_list_item(channel["name"], "Categoría: %s" % channel["group"])
        item.setProperty("IsPlayable", "true")
        if channel.get("logo"):
            item.setArt({"thumb": channel["logo"], "icon": channel["logo"]})
        play_url = _plugin_url(action="play", url=channel["url"], name=channel["name"])
        items.append((play_url, item, False))

    xbmcplugin.setContent(HANDLE, "videos")
    xbmcplugin.addDirectoryItems(HANDLE, items, len(items))
    xbmcplugin.endOfDirectory(HANDLE)
    if not filtered:
        _notify("No se encontraron canales con ese filtro")


def play_channel(url: str, name: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.netloc:
        raise ValueError("La dirección del canal no es una URL HTTP/HTTPS válida")
    item = xbmcgui.ListItem(label=name or "IPTV", path=url)
    item.setInfo("video", {"title": name or "IPTV", "mediatype": "video"})
    item.setProperty("IsPlayable", "true")
    # Deja que Kodi seleccione su reproductor/inputstream disponible.
    xbmcplugin.setResolvedUrl(HANDLE, True, item)


def main() -> None:
    action = _param("action")
    try:
        if action == "settings":
            ADDON.openSettings()
            xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=True, cacheToDisc=False)
            return
        if action == "play":
            play_channel(_param("url"), _param("name", "IPTV"))
            return
        if not action:
            show_root()
            return

        channels = _load_channels()
        if action == "categories":
            show_categories(channels)
        elif action == "group":
            show_channels(channels, group=_param("group"))
        elif action == "all":
            show_channels(channels)
        elif action == "search":
            query = xbmcgui.Dialog().input("Nombre del canal", type=xbmcgui.INPUT_ALPHANUM)
            if query:
                show_channels(channels, query=query)
            else:
                xbmcplugin.endOfDirectory(HANDLE, succeeded=True, cacheToDisc=False)
        else:
            show_root()
    except Exception as exc:  # Show a useful message instead of leaving Kodi spinning.
        xbmc.log("[%s] Error: %s" % (ADDON_ID, exc), xbmc.LOGERROR)
        xbmcgui.Dialog().ok(ADDON_NAME, "No se pudo cargar IPTV.\n\n%s" % str(exc))
        xbmcplugin.endOfDirectory(HANDLE, succeeded=False, cacheToDisc=False)


if __name__ == "__main__":
    main()
