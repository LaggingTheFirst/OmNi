# Remote Access Guide for OmNi

This guide explains how to access your OmNi instance from anywhere in the world securely, without exposing your home network ports.

## Recommended Method: Cloudflare Tunnel

We recommend **Cloudflare Tunnel** (formerly Argo Tunnel) because it's secure, free, and doesn't require port forwarding on your router.

### Prerequisites
1.  A valid domain name (you can get a cheap one or potentially a free one, or use Cloudflare's quick tunnel for testing).
2.  A [Cloudflare account](https://dash.cloudflare.com/sign-up) (Free).

### Step 1: Install Cloudflared
Download the `cloudflared` tool for your operating system:
- **Windows**: [Download cloudflared-windows-amd64.exe](https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe)
- **Linux**: See Cloudflare documentation.

### Step 2: Quick Start (Test Tunnel)
Open your terminal (CMD or PowerShell) and run:

```bash
cloudflared tunnel --url http://localhost:5000
```

Cloudflare will generate a random URL (e.g., `https://random-name.trycloudflare.com`) that tunnels directly to your local OmNi app. You can share this link with anyone!

### Step 3: Permanent Tunnel (Custom Domain)
For a permanent link like `https://omni.yourname.com`:

1.  Log in to Cloudflare Dashboard -> **Zero Trust** -> **Networks** -> **Tunnels**.
2.  Click **Create a Tunnel**.
3.  Name it (e.g., "omni-home").
4.  Choose your environment (Windows/Mac/Docker) and **copy the installation command** provided.
    - Run that command on the computer hosting OmNi.
5.  **Configure the Public Hostname**:
    - **Subdomain**: `omni` (or whatever you want)
    - **Domain**: `yourdomain.com`
    - **Service**: `http://localhost:5000`
6.  Save.

Your app is now accessible at `https://omni.yourdomain.com`!

### Security Note
Since your app is now on the public internet, ensure you have set a **Strong Admin Password** in `config.py` (or Docker environment variables).
