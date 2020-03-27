import network
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='uPY_14n', authmode=network.AUTH_WPA_WPA2_PSK)
print (ap.ifconfig())
