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

---

## ❓ Security FAQ

### Is it safe to expose OmNi to the internet?
OmNi is built with security in mind (E2EE, Argon2 hashing, secure session cookies), but exposing **any** app to the public web carries risk. We recommend using HTTPS (Cloudflare Tunnel handles this automatically) and strong passwords.

### What is a "Reverse Proxy"?
Imagine it as a security guard at the gate. A reverse proxy (like Nginx, Caddy, or Cloudflare Tunnel) sits between the user and your app, handling encryption (SSL) and filtering dangerous requests.

### Do I need to open ports on my router?
If you use **Cloudflare Tunnel**, no! It creates an outbound connection from your machine to Cloudflare, so you don't need to touch your router's firewall settings.

### What if I only want family to access it?
You can use a **VPN** like **Tailscale** or **ZeroTier**. These create a "private room" on the internet that only your invited devices can enter. If you use a VPN, you don't even need a public URL—you just use the VPN IP of your hosting machine.
