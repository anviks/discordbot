#!/usr/bin/env bash
# Install or update the bot on a server. Run as root.
#
#   sudo scripts/deploy.sh
#
# Layout:
#   /usr/local/lib/max-bot   code + .venv        root:root, read-only to the service
#   /etc/max-bot/env         secrets             root:max-bot 0640
#   /var/lib/max-bot         sqlite + chat logs  created by systemd (StateDirectory=)
set -euo pipefail

install_dir=/usr/local/lib/max-bot
config_dir=/etc/max-bot
service=max-bot

if [[ $EUID -ne 0 ]]; then
    echo "Run as root: sudo $0" >&2
    exit 1
fi

if [[ ! -d $install_dir/.git ]]; then
    echo "No checkout at $install_dir. Clone it first:" >&2
    echo "  sudo git clone <repo-url> $install_dir" >&2
    exit 1
fi

if ! command -v uv &>/dev/null; then
    echo "uv not found in root's PATH." >&2
    echo "Install it system-wide:" >&2
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sudo env UV_INSTALL_DIR=/usr/local/bin INSTALLER_NO_MODIFY_PATH=1 sh" >&2
    exit 1
fi

# Service account: no login, no home directory, nothing but an identity to own files.
if ! id -u "$service" &>/dev/null; then
    useradd --system --no-create-home --shell /usr/sbin/nologin "$service"
    echo "Created system user '$service'"
fi

git -C "$install_dir" pull --ff-only

# Sync deps at deploy time: the service itself runs against a read-only tree and
# cannot write .venv, so this must not happen at start-up.
(cd "$install_dir" && uv sync --frozen)

# Code is owned by root and never written by the service.
chown -R root:root "$install_dir"
chmod -R go-w "$install_dir"

install -d -o root -g root -m 755 "$config_dir"

seeded=false
if [[ ! -f "$config_dir/env" ]]; then
    cp "$install_dir/.env.example" "$config_dir/env"
    seeded=true
fi

# Readable by the service, writable only by root.
chown root:"$service" "$config_dir/env"
chmod 640 "$config_dir/env"

if [[ $seeded == true ]]; then
    echo "Created $config_dir/env from the example - fill it in, then re-run."
    exit 1
fi

install -m 644 "$install_dir/scripts/$service.service" "/etc/systemd/system/$service.service"
ln -sfn "$install_dir/.venv/bin/$service" "/usr/local/bin/$service"

systemctl daemon-reload
systemctl enable --now "$service"
systemctl restart "$service"

echo
systemctl --no-pager --lines=0 status "$service" || true
echo
echo "Logs: journalctl -u $service -f"
