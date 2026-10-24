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
2026-10-23T14:39:03-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=16 {"id":"eq04-no02","boot_id":122,"seq":16,"ts":1792777071,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:39:03-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=17 {"id":"eq04-no02","boot_id":122,"seq":17,"ts":1792777101,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:39:03-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=18 {"id":"eq04-no02","boot_id":122,"seq":18,"ts":1792777131,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:39:04-03:00 ufpi-iot26/eq04/no02/status online [retida]
2026-10-23T14:39:21-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=19 {"id":"eq04-no02","boot_id":122,"seq":19,"ts":1792777161,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:39:51-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=20 {"id":"eq04-no02","boot_id":122,"seq":20,"ts":1792777191,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:40:21-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=21 {"id":"eq04-no02","boot_id":122,"seq":21,"ts":1792777221,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:40:51-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=22 {"id":"eq04-no02","boot_id":122,"seq":22,"ts":1792777251,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:41:21-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=23 {"id":"eq04-no02","boot_id":122,"seq":23,"ts":1792777281,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:41:51-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=24 {"id":"eq04-no02","boot_id":122,"seq":24,"ts":1792777311,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:42:21-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=25 {"id":"eq04-no02","boot_id":122,"seq":25,"ts":1792777341,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:42:22-03:00 ufpi-iot26/eq04/no02/status offline
2026-10-23T14:42:24-03:00 ufpi-iot26/eq04/no02/status online
2026-10-23T14:42:24-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=25 {"id":"eq04-no02","boot_id":122,"seq":25,"ts":1792777341,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:42:51-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=26 {"id":"eq04-no02","boot_id":122,"seq":26,"ts":1792777370,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:43:21-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=27 {"id":"eq04-no02","boot_id":122,"seq":27,"ts":1792777400,"sensor_ok":true,"temp_c":36.3,"umid_pct":37}
2026-10-23T14:43:51-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=28 {"id":"eq04-no02","boot_id":122,"seq":28,"ts":1792777430,"sensor_ok":true,"temp_c":36.3,"umid_pct":36}
2026-10-23T14:44:21-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=29 {"id":"eq04-no02","boot_id":122,"seq":29,"ts":1792777460,"sensor_ok":true,"temp_c":36.3,"umid_pct":36}
2026-10-23T14:44:51-03:00 ufpi-iot26/eq04/no02/telemetria id=eq04-no02 boot_id=122 seq=30 {"id":"eq04-no02","boot_id":122,"seq":30,"ts":1792777490,"sensor_ok":true,"temp_c":36.3,"umid_pct":36}