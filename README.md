![flowpassage logo](content/banner/banner.png "Flowpassage")

<h1 align="center">FlowPassage - Easy Server Relaying Solution</h1>

---

### ⚠️ WARNING: Work in Progress
FlowPassage is currently under development. Features may change, and stability is not guaranteed.  

---

## What is FlowPassage?  
FlowPassage is a **lightweight server relaying solution** designed to be easier to configure than traditional relaying tools. It allows you to expose services without dealing with complex networking or port forwarding.  

---

## Key Features
- Simplifies exposing services over the internet without port forwarding.  
- Works with **most protocols that use TCP or UDP under the hood.**  
- Seamless integration with **Tailscale** or other VPN providers.  
- Quick deployment to a VPS with minimal configuration.  
- Flexible setup: define the machine and port you want to expose.  

---

## Supported Protocols

| Protocol | Supported? |
|----------|-------------|
| TCP      | ✅ Fully supported |
| UDP      | ✅ Fully supported |
| FTP      | ⚠️ Works if relayed over TCP |
| SFTP     | ⚠️ Works if relayed over TCP |
| SSH      | ⚠️ Works if relayed over TCP |
| SMB      | ⚠️ Works if relayed over TCP |
| HTTP     | ⚠️ Partially supported (native optimizations in progress) |

> **Note:** FlowPassage supports most protocols that rely on TCP or UDP transport.  
> Application-specific optimizations (like for HTTP or SSH) may be added in future releases.

---

<a href="https://www.star-history.com/#ptc0/flow-passage&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ptc0/flow-passage&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ptc0/flow-passage&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=ptc0/flow-passage&type=date&legend=top-left" />
 </picture>
</a>