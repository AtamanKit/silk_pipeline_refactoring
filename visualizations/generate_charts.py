import os
import matplotlib.pyplot as plt
from collections import Counter
from typing import List
from matplotlib.ticker import MaxNLocator
from models import NormalizedHost


def plot_vendor_distribution(hosts: List[NormalizedHost], save_dir: str = "visualizations/charts"):
    os.makedirs(save_dir, exist_ok=True)
    # vendor_counts = Counter([host.vendor for host in hosts])
    # vendor_counts = Counter(vendor for host in hosts for vendor in host.vendor)

    # Count vendor *combinations* per host
    vendor_combos = Counter(tuple(sorted(host.vendor)) for host in hosts)

    # Convert tuple keys like ('crowdstrike', 'qualys') into string labels
    labels = [' + '.join(v) for v in vendor_combos.keys()]
    values = list(vendor_combos.values())

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("Vendor Distribution")
    plt.savefig(os.path.join(save_dir, "vendor_distribution.png"))
    plt.close()


def simplify_os_name(full_os_name: str) -> str:
    """Simplify OS names for visualization clarity."""
    name = full_os_name.lower()
    if "windows server 2019" in name:
        return "Windows Server 2019"
    elif "amazon linux 2" in name:
        return "Amazon Linux 2"
    elif "ubuntu" in name:
        return "Ubuntu"
    elif "mac" in name or "ventura" in name:
        return "macOS"
    elif "windows" in name:
        return "Other Windows"
    else:
        return full_os_name.split()[0].capitalize()

def plot_os_distribution(hosts: List[NormalizedHost], save_dir: str = "visualizations/charts"):
    os.makedirs(save_dir, exist_ok=True)
    # Apply simplification
    simplified_names = [simplify_os_name(host.os) for host in hosts]
    os_counts = Counter(simplified_names)

    plt.figure(figsize=(8, 6))
    plt.bar(os_counts.keys(), os_counts.values(), color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.title("Operating System Distribution")
    plt.ylabel("Number of Hosts")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "os_distribution.png"))
    plt.close()


def plot_last_seen_timeline(hosts: List[NormalizedHost], save_dir: str = "visualizations/charts"):
    os.makedirs(save_dir, exist_ok=True)
    dates = [host.last_seen.date() for host in hosts]
    date_counts = Counter(dates)

    sorted_dates = sorted(date_counts.items())
    x, y = zip(*sorted_dates)

    plt.figure(figsize=(10, 5))
    plt.plot(x, y, marker='o', linestyle='None', color='green', markersize=10)
    plt.title("Hosts Seen Over Time")
    plt.xlabel("Date")
    plt.ylabel("Host Count")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "last_seen_timeline.png"))
    plt.close()


def generate_all_charts(hosts: List[NormalizedHost]):
    plot_vendor_distribution(hosts)
    plot_os_distribution(hosts)
    plot_last_seen_timeline(hosts)
