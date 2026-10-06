from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


def _require_public_ip(value: str) -> None:
    ip = ipaddress.ip_address(value)
    if not ip.is_global:
        raise ValueError(f"file download host resolves to a non-public address: {ip}")


def validate_public_https_url(url: str, *, resolve_dns: bool = True) -> str:
    """Validate an authorized file-param URL without allowing local/private-network targets."""
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise ValueError("file download_url must be an absolute https URL")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("file download_url must not contain embedded credentials")
    if parsed.port not in {None, 443}:
        raise ValueError("file download_url must use the default HTTPS port")

    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost"):
        raise ValueError("file download_url must not target localhost")

    try:
        _require_public_ip(host)
        return url
    except ValueError as exc:
        try:
            ipaddress.ip_address(host)
        except ValueError:
            pass
        else:
            raise exc

    if not resolve_dns:
        return url

    try:
        answers = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"file download host could not be resolved: {host}") from exc
    addresses = {answer[4][0] for answer in answers}
    if not addresses:
        raise ValueError(f"file download host resolved to no addresses: {host}")
    for address in addresses:
        _require_public_ip(address)
    return url
