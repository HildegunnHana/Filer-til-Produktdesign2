import network
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='navnet_du_vil_ha', authmode=network.AUTH_WPA_WPA2_PSK)
print (ap.ifconfig())
