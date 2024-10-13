![KrakenSDR Web Map](https://github.com/dotignore/KrakenSDR_Desktop/blob/main/media/KrakenScope.png)

------------

![KrakenSDR Web Map](https://github.com/dotignore/KrakenSDR_Desktop/blob/main/media/kraken_interface_bw.png)

![KrakenSDR Web Map](https://github.com/dotignore/KrakenSDR_Desktop/blob/main/media/structure.jpg)

Version TWO KrakenSDRs

![KrakenSDR Web Map](https://github.com/dotignore/KrakenSDR_Desktop/blob/main/media/two_kraken.gif)

Toolbar

![KrakenSDR Web Map](https://github.com/dotignore/KrakenSDR_Desktop/blob/main/media/tools.png)

- [x] LOG (Time, Freq, Name KrakenSDR, GPS, Bearing degree, Direction degree) 
------------
```python
Time: 2024-09-30T21:18:52.891722, Freq: 100 MHz, 
KrakenSDR 1: N=50.4364810212406, E=30.48805736470968, B=235°, D=174.0°
Time: 2024-09-30T21:18:52.892402, Freq: 100 MHz, 
KrakenSDR 2: N=50.47965716871645, E=30.449911826290194, B=280°, D=174.0°
..............
Time: 2024-09-30T21:18:57.759780, Freq: 100 MHz, 
KrakenSDR 1: N=50.4364810212406, E=30.48805736470968, B=235°, D=176.0°
Time: 2024-09-30T21:18:57.760440, Freq: 100 MHz, 
KrakenSDR 2: N=50.47965716871645, E=30.449911826290194, B=280°, D=176.0°
```

- [x] Write log data to DB SQLight.
  - [x] add identification **SESSION** to DB for next sort.
------------
```python
Session, Time, Freq (MHz), KrakenSDR ID, Latitude, Longitude, Bearing, Direction
(0, '2024-10-13T18:56:24.878557', 100.0, 1, 47.152155637669935, 37.51730917399983, 
180.0, 192.0)
(0, '2024-10-13T18:56:25.302166', 100.0, 2, 47.131840148609655, 37.454905671766035, 
140.0, 192.0)
(0, '2024-10-13T18:56:25.303958', 100.0, 1, 47.152155637669935, 37.51730917399983, 
180.0, 192.0)
..............
(1, '2024-10-13T18:56:26.609921', 102.5, 2, 47.131840148609655, 37.454905671766035, 
140.0, 201.0)
(1, '2024-10-13T18:56:26.611729', 102.5, 1, 47.152155637669935, 37.51730917399983, 
180.0, 201.0)
(1, '2024-10-13T18:56:27.056610', 102.5, 2, 47.131840148609655, 37.454905671766035,
140.0, 203.0)
```

**In development stage next**:
- [ ] Data display on the map.
- [ ] Sorting: by date, by frequency, by region on the map.
  - [ ] average DF
  - [ ] Discarding incorrect data.
  - [ ] Get frequency from Uniden.


## URL: [Two KrakenSDRs web](https://github.com/dotignore/KrakenSDR_Desktop/tree/main/two_KrakenSDRs_web "Two KrakenSDRs web")

------------

Version ONE KrakenSDR

![KrakenSDR Web Map](https://github.com/dotignore/KrakenSDR_Desktop/blob/main/one_krakenSDR_web/map.png)

## URL: [ONE KrakenSDRs web](https://github.com/dotignore/KrakenSDR_Desktop/tree/main/one_krakenSDR_web "Two KrakenSDRs web")

------------

# KrakenScope

KrakenSDR tech specs
- Obtaining the first bearing from a cold start: 20 to 50 seconds
- Obtaining a bearing when retuning outside the 2.4 MHz spectrum band: 5 seconds
- Obtaining a bearing within the 2.4 MHz spectrum band: 2 seconds
- Bearing update: 0.44 seconds
-
- 24 MHz to 1766 MHz tuning Range (standard R820T2 RTL-SDR range, and possibly higher with hacked drivers)
- 8.3 degrees for the circular array, and 3.4 degrees for the linear array

**My contacts: hc158b@gmail.com, https://x.com/VolodymyrTr** 

------------