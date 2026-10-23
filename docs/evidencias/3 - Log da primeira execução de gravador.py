Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

PS C:\Users\zacns\OneDrive\Documentos\Arduino\higrolar\gravador> py gravador.py --host i5c91926.ala.us-east-1.emqxsl.com --usuario higrolar-gravador
Senha MQTT de higrolar-gravador:
[gravador] broker i5c91926.ala.us-east-1.emqxsl.com:8883 (TLS com validacao)
[gravador] usuario=higrolar-gravador, client_id=ufpi-iot26-eq04-gravador
[gravador] arquivo=C:\Users\zacns\OneDrive\Documentos\Arduino\higrolar\dados\mensagens.csv
[gravador] sessao persistente=True
[gravador] CSV inclui id, boot_id, seq; Ctrl+C para terminar
[mqtt] conectado; sessao anterior: existia
[mqtt] SUBSCRIBE QoS 1: ufpi-iot26/eq04/no02/telemetria (mid=1)
[mqtt] SUBSCRIBE QoS 1: ufpi-iot26/eq04/no02/status (mid=2)
[mqtt] SUBSCRIBE QoS 1: ufpi-iot26/eq04/no02/config (mid=3)
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=120 seq=19 {"id":"eq04-no02","boot_id":120,"seq":19,"ts":1792776265,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=120 seq=20 {"id":"eq04-no02","boot_id":120,"seq":20,"ts":1792776295,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/status offline
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/status online
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=1 {"id":"eq04-no02","boot_id":121,"seq":1,"ts":1792776314,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=2 {"id":"eq04-no02","boot_id":121,"seq":2,"ts":1792776321,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=3 {"id":"eq04-no02","boot_id":121,"seq":3,"ts":1792776325,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=4 {"id":"eq04-no02","boot_id":121,"seq":4,"ts":1792776331,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=5 {"id":"eq04-no02","boot_id":121,"seq":5,"ts":1792776335,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=6 {"id":"eq04-no02","boot_id":121,"seq":6,"ts":1792776341,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=7 {"id":"eq04-no02","boot_id":121,"seq":7,"ts":1792776345,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=8 {"id":"eq04-no02","boot_id":121,"seq":8,"ts":1792776351,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/config {
  "periodo_s": 30
}
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=9 {"id":"eq04-no02","boot_id":121,"seq":9,"ts":1792776381,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=10 {"id":"eq04-no02","boot_id":121,"seq":10,"ts":1792776411,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=11 {"id":"eq04-no02","boot_id":121,"seq":11,"ts":1792776441,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:27:27-03:00 ufpi-iot26/eq04/no02/status online [retida]
2026-10-23T14:27:51-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=12 {"id":"eq04-no02","boot_id":121,"seq":12,"ts":1792776471,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:28:21-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=13 {"id":"eq04-no02","boot_id":121,"seq":13,"ts":1792776501,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:29:16-03:00 ufpi-iot26/eq04/no02/status offline
2026-10-23T14:32:28-03:00 ufpi-iot26/eq04/no02/status online
2026-10-23T14:32:28-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=14 {"id":"eq04-no02","boot_id":121,"seq":14,"ts":1792776531,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:32:28-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=15 {"id":"eq04-no02","boot_id":121,"seq":15,"ts":1792776560,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:32:28-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=16 {"id":"eq04-no02","boot_id":121,"seq":16,"ts":1792776590,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:32:29-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=17 {"id":"eq04-no02","boot_id":121,"seq":17,"ts":1792776620,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:32:29-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=18 {"id":"eq04-no02","boot_id":121,"seq":18,"ts":1792776650,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:32:29-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=19 {"id":"eq04-no02","boot_id":121,"seq":19,"ts":1792776680,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:32:29-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=20 {"id":"eq04-no02","boot_id":121,"seq":20,"ts":1792776710,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:32:29-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=21 {"id":"eq04-no02","boot_id":121,"seq":21,"ts":1792776736,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:32:55-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=22 {"id":"eq04-no02","boot_id":121,"seq":22,"ts":1792776773,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:33:25-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=23 {"id":"eq04-no02","boot_id":121,"seq":23,"ts":1792776803,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:33:55-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=121 seq=24 {"id":"eq04-no02","boot_id":121,"seq":24,"ts":1792776833,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:34:06-03:00 ufpi-iot26/eq04/no02/status offline
2026-10-23T14:34:06-03:00 ufpi-iot26/eq04/no02/status online
2026-10-23T14:34:06-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=1 {"id":"eq04-no02","boot_id":122,"seq":1,"ts":null,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:34:11-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=2 {"id":"eq04-no02","boot_id":122,"seq":2,"ts":1792776851,"sensor_ok":true,"temp_c":36.3,"umid_pct":38}
2026-10-23T14:34:16-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=3 {"id":"eq04-no02","boot_id":122,"seq":3,"ts":1792776855,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:34:21-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=4 {"id":"eq04-no02","boot_id":122,"seq":4,"ts":1792776861,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:34:26-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=5 {"id":"eq04-no02","boot_id":122,"seq":5,"ts":1792776865,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:34:31-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=6 {"id":"eq04-no02","boot_id":122,"seq":6,"ts":1792776871,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:34:36-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=7 {"id":"eq04-no02","boot_id":122,"seq":7,"ts":1792776875,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:34:41-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=8 {"id":"eq04-no02","boot_id":122,"seq":8,"ts":1792776881,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:34:46-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=9 {"id":"eq04-no02","boot_id":122,"seq":9,"ts":1792776885,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:34:51-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=10 {"id":"eq04-no02","boot_id":122,"seq":10,"ts":1792776891,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:34:55-03:00 ufpi-iot26/eq04/no02/config {
  "periodo_s": 30
}
2026-10-23T14:35:21-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=11 {"id":"eq04-no02","boot_id":122,"seq":11,"ts":1792776921,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:35:51-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=12 {"id":"eq04-no02","boot_id":122,"seq":12,"ts":1792776951,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}