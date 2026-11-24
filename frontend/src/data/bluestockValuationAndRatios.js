// Bluestock Intelligence · Audited Valuation Multiples & Computed Financial Ratios
// Ingested from market_cap.xlsx (552 records) and financial_ratios.xlsx (1,184 records)
// In accordance with Project Execution Plan Technical Specification v1.0

export const RAW_MARKET_CAP_DATA = [
  {id:1,company_id:"ABB",year:2019,market_cap_crore:844312.98,enterprise_value_crore:814410.48,pe_ratio:19.29,pb_ratio:14.26,ev_ebitda:22.84,dividend_yield_pct:0.84},
  {id:2,company_id:"ABB",year:2020,market_cap_crore:923674.33,enterprise_value_crore:1120679.72,pe_ratio:67.54,pb_ratio:13.03,ev_ebitda:24.93,dividend_yield_pct:3.9},
  {id:3,company_id:"ABB",year:2021,market_cap_crore:1020674.09,enterprise_value_crore:1166450.81,pe_ratio:62.63,pb_ratio:6.67,ev_ebitda:7.58,dividend_yield_pct:1.58},
  {id:4,company_id:"ABB",year:2022,market_cap_crore:1185994.82,enterprise_value_crore:1158637.42,pe_ratio:18.68,pb_ratio:4.75,ev_ebitda:6.12,dividend_yield_pct:3.35},
  {id:5,company_id:"ABB",year:2023,market_cap_crore:1161513.28,enterprise_value_crore:1103083.77,pe_ratio:58.34,pb_ratio:12.72,ev_ebitda:5.7,dividend_yield_pct:1.05},
  {id:6,company_id:"ABB",year:2024,market_cap_crore:1536236.24,enterprise_value_crore:1619349.16,pe_ratio:75.58,pb_ratio:4.48,ev_ebitda:12.63,dividend_yield_pct:0.96},
  {id:7,company_id:"ADANIENSOL",year:2019,market_cap_crore:171905.69,enterprise_value_crore:222090.81,pe_ratio:76.72,pb_ratio:12.85,ev_ebitda:34.64,dividend_yield_pct:2.97},
  {id:8,company_id:"ADANIENSOL",year:2020,market_cap_crore:217135.25,enterprise_value_crore:213517.12,pe_ratio:35.93,pb_ratio:9.79,ev_ebitda:35.62,dividend_yield_pct:2.97},
  {id:9,company_id:"ADANIENSOL",year:2021,market_cap_crore:275655.59,enterprise_value_crore:300348.76,pe_ratio:59.65,pb_ratio:14.71,ev_ebitda:10.37,dividend_yield_pct:4.17},
  {id:10,company_id:"ADANIENSOL",year:2022,market_cap_crore:306303.52,enterprise_value_crore:354481.15,pe_ratio:71.21,pb_ratio:6.44,ev_ebitda:19.65,dividend_yield_pct:2.37},
  {id:11,company_id:"ADANIENSOL",year:2023,market_cap_crore:263283.51,enterprise_value_crore:289260.77,pe_ratio:28.96,pb_ratio:13.96,ev_ebitda:8.07,dividend_yield_pct:2.07},
  {id:12,company_id:"ADANIENSOL",year:2024,market_cap_crore:348517.36,enterprise_value_crore:439276.19,pe_ratio:58.5,pb_ratio:9.05,ev_ebitda:14.83,dividend_yield_pct:1.65},
  {id:13,company_id:"ADANIENT",year:2019,market_cap_crore:173718.83,enterprise_value_crore:178851.86,pe_ratio:56.08,pb_ratio:5.69,ev_ebitda:21.25,dividend_yield_pct:2.5},
  {id:14,company_id:"ADANIENT",year:2020,market_cap_crore:217309.44,enterprise_value_crore:213933.01,pe_ratio:36.71,pb_ratio:2.39,ev_ebitda:7.65,dividend_yield_pct:2.72},
  {id:15,company_id:"ADANIENT",year:2021,market_cap_crore:205258.66,enterprise_value_crore:189642.53,pe_ratio:72.59,pb_ratio:8.25,ev_ebitda:9.71,dividend_yield_pct:0.24},
  {id:16,company_id:"ADANIENT",year:2022,market_cap_crore:186771.02,enterprise_value_crore:203306.77,pe_ratio:56.13,pb_ratio:9.8,ev_ebitda:10.05,dividend_yield_pct:2.85},
  {id:17,company_id:"ADANIENT",year:2023,market_cap_crore:196563.95,enterprise_value_crore:213448.3,pe_ratio:65.7,pb_ratio:5.32,ev_ebitda:10.14,dividend_yield_pct:3.93},
  {id:18,company_id:"ADANIENT",year:2024,market_cap_crore:187927.97,enterprise_value_crore:191237.75,pe_ratio:58.87,pb_ratio:10.41,ev_ebitda:33.01,dividend_yield_pct:0.83},
  {id:19,company_id:"ADANIGREEN",year:2019,market_cap_crore:485373.12,enterprise_value_crore:541878.15,pe_ratio:29.07,pb_ratio:10.49,ev_ebitda:5.01,dividend_yield_pct:0.27},
  {id:20,company_id:"ADANIGREEN",year:2020,market_cap_crore:517543.72,enterprise_value_crore:664150.23,pe_ratio:72.14,pb_ratio:14.91,ev_ebitda:19.59,dividend_yield_pct:0.21},
  {id:21,company_id:"ADANIGREEN",year:2021,market_cap_crore:519085,enterprise_value_crore:607489.51,pe_ratio:17.73,pb_ratio:4.85,ev_ebitda:6.97,dividend_yield_pct:2.14},
  {id:22,company_id:"ADANIGREEN",year:2022,market_cap_crore:495446.05,enterprise_value_crore:463984.83,pe_ratio:37.61,pb_ratio:5.59,ev_ebitda:23.81,dividend_yield_pct:3.37},
  {id:23,company_id:"ADANIGREEN",year:2023,market_cap_crore:449015.01,enterprise_value_crore:546204.41,pe_ratio:9.89,pb_ratio:6.92,ev_ebitda:25.56,dividend_yield_pct:4.31},
  {id:24,company_id:"ADANIGREEN",year:2024,market_cap_crore:510512.78,enterprise_value_crore:491878.9,pe_ratio:45.26,pb_ratio:6.24,ev_ebitda:21.78,dividend_yield_pct:0.89},
  {id:25,company_id:"ADANIPORTS",year:2019,market_cap_crore:697221.18,enterprise_value_crore:835004.1,pe_ratio:50.76,pb_ratio:1.64,ev_ebitda:36.14,dividend_yield_pct:2.77},
  {id:26,company_id:"ADANIPORTS",year:2020,market_cap_crore:702836.27,enterprise_value_crore:645384.3,pe_ratio:53.52,pb_ratio:5.91,ev_ebitda:36.77,dividend_yield_pct:0.16},
  {id:27,company_id:"ADANIPORTS",year:2021,market_cap_crore:611152.14,enterprise_value_crore:782103.44,pe_ratio:77.47,pb_ratio:0.9,ev_ebitda:30.06,dividend_yield_pct:1},
  {id:28,company_id:"ADANIPORTS",year:2022,market_cap_crore:733808.16,enterprise_value_crore:915420.63,pe_ratio:15.26,pb_ratio:3.96,ev_ebitda:5.84,dividend_yield_pct:0.2},
  {id:29,company_id:"ADANIPORTS",year:2023,market_cap_crore:634603.85,enterprise_value_crore:774389.91,pe_ratio:29.48,pb_ratio:7.65,ev_ebitda:32.57,dividend_yield_pct:2.23},
  {id:30,company_id:"ADANIPORTS",year:2024,market_cap_crore:675598.01,enterprise_value_crore:611165.74,pe_ratio:48.9,pb_ratio:2.31,ev_ebitda:31.76,dividend_yield_pct:1.16},
  {id:31,company_id:"ADANIPOWER",year:2019,market_cap_crore:1188256.85,enterprise_value_crore:1362538.77,pe_ratio:27.22,pb_ratio:4.37,ev_ebitda:35.21,dividend_yield_pct:0.06},
  {id:32,company_id:"ADANIPOWER",year:2020,market_cap_crore:1117866.08,enterprise_value_crore:1278915.22,pe_ratio:66.83,pb_ratio:5.7,ev_ebitda:27.87,dividend_yield_pct:2.51},
  {id:33,company_id:"ADANIPOWER",year:2021,market_cap_crore:986259.76,enterprise_value_crore:1132916.67,pe_ratio:66.6,pb_ratio:14.89,ev_ebitda:6.04,dividend_yield_pct:2.97},
  {id:34,company_id:"ADANIPOWER",year:2022,market_cap_crore:1042747.57,enterprise_value_crore:942555.33,pe_ratio:52.23,pb_ratio:2.28,ev_ebitda:18.25,dividend_yield_pct:1.18},
  {id:35,company_id:"ADANIPOWER",year:2023,market_cap_crore:1074636.56,enterprise_value_crore:1178960.38,pe_ratio:33.86,pb_ratio:8.51,ev_ebitda:13.35,dividend_yield_pct:2.86},
  {id:36,company_id:"ADANIPOWER",year:2024,market_cap_crore:1372183.55,enterprise_value_crore:1357949.64,pe_ratio:44.57,pb_ratio:9.91,ev_ebitda:24.76,dividend_yield_pct:1.65},
  {id:37,company_id:"AMBUJACEM",year:2019,market_cap_crore:833955.32,enterprise_value_crore:873953.9,pe_ratio:46.35,pb_ratio:0.8,ev_ebitda:22.77,dividend_yield_pct:2.94},
  {id:38,company_id:"AMBUJACEM",year:2020,market_cap_crore:1025434.68,enterprise_value_crore:969394.29,pe_ratio:79.32,pb_ratio:9.29,ev_ebitda:17.71,dividend_yield_pct:1.12},
  {id:39,company_id:"AMBUJACEM",year:2021,market_cap_crore:1165353.63,enterprise_value_crore:1459820.61,pe_ratio:45.48,pb_ratio:10.09,ev_ebitda:17.52,dividend_yield_pct:1.75},
  {id:40,company_id:"AMBUJACEM",year:2022,market_cap_crore:1157298.18,enterprise_value_crore:1368221.47,pe_ratio:33.86,pb_ratio:3.27,ev_ebitda:17.93,dividend_yield_pct:3.84},
  {id:41,company_id:"AMBUJACEM",year:2023,market_cap_crore:1410892.33,enterprise_value_crore:1458659.98,pe_ratio:73.29,pb_ratio:1.59,ev_ebitda:6.74,dividend_yield_pct:0.57},
  {id:42,company_id:"AMBUJACEM",year:2024,market_cap_crore:1281411.04,enterprise_value_crore:1198290.68,pe_ratio:55.62,pb_ratio:9.21,ev_ebitda:27.67,dividend_yield_pct:3.1},
  {id:43,company_id:"APOLLOHOSP",year:2019,market_cap_crore:1083786.88,enterprise_value_crore:1245185.95,pe_ratio:49.76,pb_ratio:14.18,ev_ebitda:13.13,dividend_yield_pct:0.26},
  {id:44,company_id:"APOLLOHOSP",year:2020,market_cap_crore:1275343.54,enterprise_value_crore:1525399.05,pe_ratio:28.39,pb_ratio:8.78,ev_ebitda:7.08,dividend_yield_pct:4.32},
  {id:45,company_id:"APOLLOHOSP",year:2021,market_cap_crore:1154138.06,enterprise_value_crore:1069918.55,pe_ratio:11.18,pb_ratio:6.7,ev_ebitda:8.4,dividend_yield_pct:3.35},
  {id:46,company_id:"APOLLOHOSP",year:2022,market_cap_crore:1499729.8,enterprise_value_crore:1505860.05,pe_ratio:53.27,pb_ratio:1.11,ev_ebitda:18.53,dividend_yield_pct:1.32},
  {id:47,company_id:"APOLLOHOSP",year:2023,market_cap_crore:1446203.76,enterprise_value_crore:1674544,pe_ratio:17.38,pb_ratio:12.98,ev_ebitda:28.27,dividend_yield_pct:3.2},
  {id:48,company_id:"APOLLOHOSP",year:2024,market_cap_crore:1905622.43,enterprise_value_crore:2433382.94,pe_ratio:47.72,pb_ratio:7.68,ev_ebitda:16.74,dividend_yield_pct:3.22},
  {id:49,company_id:"ASIANPAINT",year:2019,market_cap_crore:1065817.17,enterprise_value_crore:1060968.11,pe_ratio:30.34,pb_ratio:5.08,ev_ebitda:33.21,dividend_yield_pct:0.45},
  {id:50,company_id:"ASIANPAINT",year:2020,market_cap_crore:1148763.92,enterprise_value_crore:1230363.26,pe_ratio:13.27,pb_ratio:6.46,ev_ebitda:22.97,dividend_yield_pct:0.29},
  {id:51,company_id:"ASIANPAINT",year:2021,market_cap_crore:1269304.94,enterprise_value_crore:1629400.62,pe_ratio:78.48,pb_ratio:8.21,ev_ebitda:23.03,dividend_yield_pct:1.28},
  {id:52,company_id:"ASIANPAINT",year:2022,market_cap_crore:1711731,enterprise_value_crore:1728320.53,pe_ratio:40.61,pb_ratio:0.54,ev_ebitda:17.22,dividend_yield_pct:0.32},
  {id:53,company_id:"ASIANPAINT",year:2023,market_cap_crore:2091585.31,enterprise_value_crore:2351790.62,pe_ratio:49.2,pb_ratio:4.65,ev_ebitda:33.52,dividend_yield_pct:0.01},
  {id:54,company_id:"ASIANPAINT",year:2024,market_cap_crore:2126725.18,enterprise_value_crore:2475080.63,pe_ratio:73.37,pb_ratio:3.9,ev_ebitda:23.94,dividend_yield_pct:2.42},
  {id:55,company_id:"ATGL",year:2019,market_cap_crore:1148243.4,enterprise_value_crore:1228379.56,pe_ratio:21.14,pb_ratio:0.81,ev_ebitda:10.15,dividend_yield_pct:4.39},
  {id:56,company_id:"ATGL",year:2020,market_cap_crore:1099356.08,enterprise_value_crore:1400593.18,pe_ratio:22.78,pb_ratio:14,ev_ebitda:27.91,dividend_yield_pct:0.51},
  {id:57,company_id:"ATGL",year:2021,market_cap_crore:1254318.65,enterprise_value_crore:1288694.02,pe_ratio:35.59,pb_ratio:6.88,ev_ebitda:19.79,dividend_yield_pct:2.99},
  {id:58,company_id:"ATGL",year:2022,market_cap_crore:1548060.05,enterprise_value_crore:1597088.78,pe_ratio:74.55,pb_ratio:14.11,ev_ebitda:6.42,dividend_yield_pct:0.07},
  {id:59,company_id:"ATGL",year:2023,market_cap_crore:1644865.15,enterprise_value_crore:1868991.35,pe_ratio:28.01,pb_ratio:4.26,ev_ebitda:28.74,dividend_yield_pct:2.71},
  {id:60,company_id:"ATGL",year:2024,market_cap_crore:1535602.41,enterprise_value_crore:1925338.89,pe_ratio:56.96,pb_ratio:5.76,ev_ebitda:28.93,dividend_yield_pct:0.51},
  {id:61,company_id:"AXISBANK",year:2019,market_cap_crore:658857.1,enterprise_value_crore:603890.3,pe_ratio:32.36,pb_ratio:2.69,ev_ebitda:27.17,dividend_yield_pct:3.03},
  {id:62,company_id:"AXISBANK",year:2020,market_cap_crore:609012.03,enterprise_value_crore:554106.67,pe_ratio:65.08,pb_ratio:0.53,ev_ebitda:17.04,dividend_yield_pct:2.23},
  {id:63,company_id:"AXISBANK",year:2021,market_cap_crore:766941.69,enterprise_value_crore:947497.75,pe_ratio:60.2,pb_ratio:4.08,ev_ebitda:30.21,dividend_yield_pct:1.11},
  {id:64,company_id:"AXISBANK",year:2022,market_cap_crore:734196.42,enterprise_value_crore:821456.53,pe_ratio:56.88,pb_ratio:1.27,ev_ebitda:7.1,dividend_yield_pct:3.53},
  {id:65,company_id:"AXISBANK",year:2023,market_cap_crore:939586.86,enterprise_value_crore:1072798.07,pe_ratio:38.88,pb_ratio:12.76,ev_ebitda:30.51,dividend_yield_pct:2.61},
  {id:66,company_id:"AXISBANK",year:2024,market_cap_crore:948868.63,enterprise_value_crore:929130.29,pe_ratio:38.14,pb_ratio:4.66,ev_ebitda:16.87,dividend_yield_pct:2.32},
  {id:85,company_id:"BAJFINANCE",year:2019,market_cap_crore:865823.64,enterprise_value_crore:997880.37,pe_ratio:58.62,pb_ratio:5.53,ev_ebitda:16.56,dividend_yield_pct:1.21},
  {id:86,company_id:"BAJFINANCE",year:2020,market_cap_crore:973552.26,enterprise_value_crore:1016449.19,pe_ratio:46.9,pb_ratio:6.39,ev_ebitda:34.29,dividend_yield_pct:0.33},
  {id:87,company_id:"BAJFINANCE",year:2021,market_cap_crore:1106057.88,enterprise_value_crore:1250121.36,pe_ratio:35.63,pb_ratio:6.6,ev_ebitda:33,dividend_yield_pct:1.26},
  {id:88,company_id:"BAJFINANCE",year:2022,market_cap_crore:1422060.71,enterprise_value_crore:1789716.47,pe_ratio:54.84,pb_ratio:11.71,ev_ebitda:26.45,dividend_yield_pct:2.36},
  {id:89,company_id:"BAJFINANCE",year:2023,market_cap_crore:1896088.83,enterprise_value_crore:1920855.51,pe_ratio:19.1,pb_ratio:4.67,ev_ebitda:26.51,dividend_yield_pct:0.83},
  {id:90,company_id:"BAJFINANCE",year:2024,market_cap_crore:2473271.58,enterprise_value_crore:2632574.41,pe_ratio:69.2,pb_ratio:4.11,ev_ebitda:15.96,dividend_yield_pct:0.27},
  {id:229,company_id:"HDFCBANK",year:2019,market_cap_crore:578281.57,enterprise_value_crore:743657.34,pe_ratio:63.58,pb_ratio:0.79,ev_ebitda:38.51,dividend_yield_pct:3.49},
  {id:230,company_id:"HDFCBANK",year:2020,market_cap_crore:534671.83,enterprise_value_crore:497530.99,pe_ratio:30.19,pb_ratio:9.55,ev_ebitda:26.58,dividend_yield_pct:1.24},
  {id:231,company_id:"HDFCBANK",year:2021,market_cap_crore:573615.98,enterprise_value_crore:564871.82,pe_ratio:11.64,pb_ratio:8,ev_ebitda:17.14,dividend_yield_pct:2.44},
  {id:232,company_id:"HDFCBANK",year:2022,market_cap_crore:759039.45,enterprise_value_crore:726665,pe_ratio:8.14,pb_ratio:1.61,ev_ebitda:21.19,dividend_yield_pct:3.18},
  {id:233,company_id:"HDFCBANK",year:2023,market_cap_crore:865594.78,enterprise_value_crore:950386.57,pe_ratio:33.49,pb_ratio:4.99,ev_ebitda:18.17,dividend_yield_pct:2.75},
  {id:234,company_id:"HDFCBANK",year:2024,market_cap_crore:808359.03,enterprise_value_crore:976938.14,pe_ratio:49.42,pb_ratio:4.4,ev_ebitda:22.54,dividend_yield_pct:4.33},
  {id:259,company_id:"ICICIBANK",year:2019,market_cap_crore:634101.51,enterprise_value_crore:817754.59,pe_ratio:75.38,pb_ratio:9.81,ev_ebitda:5.65,dividend_yield_pct:3.37},
  {id:260,company_id:"ICICIBANK",year:2020,market_cap_crore:645375.01,enterprise_value_crore:681072.05,pe_ratio:19.43,pb_ratio:8.09,ev_ebitda:31.06,dividend_yield_pct:1.23},
  {id:261,company_id:"ICICIBANK",year:2021,market_cap_crore:851486.14,enterprise_value_crore:832663.82,pe_ratio:12.77,pb_ratio:9.84,ev_ebitda:34.73,dividend_yield_pct:4.29},
  {id:262,company_id:"ICICIBANK",year:2022,market_cap_crore:1050380.96,enterprise_value_crore:1029226.29,pe_ratio:78.39,pb_ratio:13.83,ev_ebitda:10.71,dividend_yield_pct:2.51},
  {id:263,company_id:"ICICIBANK",year:2023,market_cap_crore:1184576.28,enterprise_value_crore:1275805.13,pe_ratio:78.87,pb_ratio:1.36,ev_ebitda:26.95,dividend_yield_pct:0.92},
  {id:264,company_id:"ICICIBANK",year:2024,market_cap_crore:1319221.86,enterprise_value_crore:1598760.1,pe_ratio:25.76,pb_ratio:6.2,ev_ebitda:38.28,dividend_yield_pct:3.43},
  {id:289,company_id:"INFY",year:2019,market_cap_crore:473902.69,enterprise_value_crore:535599.26,pe_ratio:32.63,pb_ratio:10.31,ev_ebitda:30.95,dividend_yield_pct:2.63},
  {id:290,company_id:"INFY",year:2020,market_cap_crore:468232.33,enterprise_value_crore:516667.75,pe_ratio:26.14,pb_ratio:13.59,ev_ebitda:31.82,dividend_yield_pct:2.22},
  {id:291,company_id:"INFY",year:2021,market_cap_crore:624026.61,enterprise_value_crore:698099.93,pe_ratio:31.65,pb_ratio:1.88,ev_ebitda:24.03,dividend_yield_pct:3.87},
  {id:292,company_id:"INFY",year:2022,market_cap_crore:800850.39,enterprise_value_crore:914432.46,pe_ratio:36.33,pb_ratio:9.93,ev_ebitda:31.67,dividend_yield_pct:1.85},
  {id:293,company_id:"INFY",year:2023,market_cap_crore:871427,enterprise_value_crore:1021527.28,pe_ratio:71.12,pb_ratio:11.97,ev_ebitda:5.78,dividend_yield_pct:0.56},
  {id:294,company_id:"INFY",year:2024,market_cap_crore:1112279.92,enterprise_value_crore:1372029.68,pe_ratio:35.99,pb_ratio:8.97,ev_ebitda:36.7,dividend_yield_pct:4.1},
  {id:313,company_id:"ITC",year:2019,market_cap_crore:215793.67,enterprise_value_crore:211845.82,pe_ratio:69.58,pb_ratio:1.15,ev_ebitda:17.46,dividend_yield_pct:2.84},
  {id:314,company_id:"ITC",year:2020,market_cap_crore:281943.95,enterprise_value_crore:351639.75,pe_ratio:72.45,pb_ratio:1.41,ev_ebitda:34.43,dividend_yield_pct:3.51},
  {id:315,company_id:"ITC",year:2021,market_cap_crore:366869.92,enterprise_value_crore:375906.12,pe_ratio:73.65,pb_ratio:6.34,ev_ebitda:27.19,dividend_yield_pct:1.91},
  {id:316,company_id:"ITC",year:2022,market_cap_crore:390285.11,enterprise_value_crore:436594.31,pe_ratio:33.63,pb_ratio:11.99,ev_ebitda:27.18,dividend_yield_pct:3.1},
  {id:317,company_id:"ITC",year:2023,market_cap_crore:376827.06,enterprise_value_crore:485289.24,pe_ratio:55.53,pb_ratio:3.36,ev_ebitda:31.27,dividend_yield_pct:0.78},
  {id:318,company_id:"ITC",year:2024,market_cap_crore:332245.58,enterprise_value_crore:369131.93,pe_ratio:47.85,pb_ratio:3.24,ev_ebitda:17.19,dividend_yield_pct:4.26},
  {id:349,company_id:"LICI",year:2019,market_cap_crore:166637.32,enterprise_value_crore:173087.14,pe_ratio:53.3,pb_ratio:0.6,ev_ebitda:39.37,dividend_yield_pct:0.77},
  {id:350,company_id:"LICI",year:2020,market_cap_crore:196576.3,enterprise_value_crore:233201.16,pe_ratio:20.36,pb_ratio:2.12,ev_ebitda:10.34,dividend_yield_pct:1.11},
  {id:351,company_id:"LICI",year:2021,market_cap_crore:183625.08,enterprise_value_crore:214767.85,pe_ratio:38.3,pb_ratio:8.3,ev_ebitda:6.66,dividend_yield_pct:3.88},
  {id:352,company_id:"LICI",year:2022,market_cap_crore:171741.93,enterprise_value_crore:179309.03,pe_ratio:13.18,pb_ratio:2.48,ev_ebitda:28.3,dividend_yield_pct:3.12},
  {id:353,company_id:"LICI",year:2023,market_cap_crore:204112.31,enterprise_value_crore:228780.25,pe_ratio:76.58,pb_ratio:7.85,ev_ebitda:20.73,dividend_yield_pct:1.11},
  {id:354,company_id:"LICI",year:2024,market_cap_crore:183583.67,enterprise_value_crore:205478.22,pe_ratio:30.67,pb_ratio:8.1,ev_ebitda:12.21,dividend_yield_pct:3.77},
  {id:379,company_id:"MARUTI",year:2019,market_cap_crore:1445154.02,enterprise_value_crore:1428864,pe_ratio:65.97,pb_ratio:4.77,ev_ebitda:37.75,dividend_yield_pct:1.13},
  {id:380,company_id:"MARUTI",year:2020,market_cap_crore:1349572.01,enterprise_value_crore:1480925.31,pe_ratio:11.64,pb_ratio:1.03,ev_ebitda:22.36,dividend_yield_pct:0.97},
  {id:381,company_id:"MARUTI",year:2021,market_cap_crore:1153447.24,enterprise_value_crore:1174696.92,pe_ratio:42.37,pb_ratio:6.22,ev_ebitda:9.74,dividend_yield_pct:2.61},
  {id:382,company_id:"MARUTI",year:2022,market_cap_crore:1390095.96,enterprise_value_crore:1626712.07,pe_ratio:36.35,pb_ratio:2.5,ev_ebitda:22.48,dividend_yield_pct:4.01},
  {id:383,company_id:"MARUTI",year:2023,market_cap_crore:1507366.44,enterprise_value_crore:1474615.02,pe_ratio:14.7,pb_ratio:14.19,ev_ebitda:31.01,dividend_yield_pct:1.41},
  {id:384,company_id:"MARUTI",year:2024,market_cap_crore:1503863.63,enterprise_value_crore:1891991.87,pe_ratio:20.78,pb_ratio:8.26,ev_ebitda:29.97,dividend_yield_pct:1.78},
  {id:409,company_id:"NTPC",year:2019,market_cap_crore:636264.32,enterprise_value_crore:742188.74,pe_ratio:33.8,pb_ratio:0.79,ev_ebitda:20.37,dividend_yield_pct:1.01},
  {id:410,company_id:"NTPC",year:2020,market_cap_crore:549989.15,enterprise_value_crore:598573.64,pe_ratio:22.83,pb_ratio:7.06,ev_ebitda:14.72,dividend_yield_pct:2.72},
  {id:411,company_id:"NTPC",year:2021,market_cap_crore:739976.68,enterprise_value_crore:827954.56,pe_ratio:54.58,pb_ratio:13.83,ev_ebitda:18.09,dividend_yield_pct:0.75},
  {id:412,company_id:"NTPC",year:2022,market_cap_crore:733611.88,enterprise_value_crore:778448.75,pe_ratio:54.44,pb_ratio:0.57,ev_ebitda:34.87,dividend_yield_pct:0.34},
  {id:413,company_id:"NTPC",year:2023,market_cap_crore:953935.75,enterprise_value_crore:1220821.99,pe_ratio:79.29,pb_ratio:12.24,ev_ebitda:9.96,dividend_yield_pct:3.18},
  {id:414,company_id:"NTPC",year:2024,market_cap_crore:907823.11,enterprise_value_crore:1142814.16,pe_ratio:30.8,pb_ratio:5.24,ev_ebitda:37.12,dividend_yield_pct:0.06},
  {id:451,company_id:"RELIANCE",year:2019,market_cap_crore:648684.98,enterprise_value_crore:791997.19,pe_ratio:42.66,pb_ratio:12.4,ev_ebitda:33.86,dividend_yield_pct:1.43},
  {id:452,company_id:"RELIANCE",year:2020,market_cap_crore:552791.93,enterprise_value_crore:699004.44,pe_ratio:62.77,pb_ratio:2.06,ev_ebitda:29.56,dividend_yield_pct:0.09},
  {id:453,company_id:"RELIANCE",year:2021,market_cap_crore:477545.63,enterprise_value_crore:530232.91,pe_ratio:14.91,pb_ratio:14.48,ev_ebitda:36.28,dividend_yield_pct:2.92},
  {id:454,company_id:"RELIANCE",year:2022,market_cap_crore:421125.76,enterprise_value_crore:433731.78,pe_ratio:34.76,pb_ratio:7.47,ev_ebitda:10.91,dividend_yield_pct:2.6},
  {id:455,company_id:"RELIANCE",year:2023,market_cap_crore:449714.02,enterprise_value_crore:575147.7,pe_ratio:75.41,pb_ratio:8.7,ev_ebitda:27.55,dividend_yield_pct:0.62},
  {id:456,company_id:"RELIANCE",year:2024,market_cap_crore:432472.71,enterprise_value_crore:545039.37,pe_ratio:58.34,pb_ratio:3.25,ev_ebitda:24.96,dividend_yield_pct:4.21},
  {id:463,company_id:"SBIN",year:2019,market_cap_crore:1482417.4,enterprise_value_crore:1684030.56,pe_ratio:28.31,pb_ratio:2.13,ev_ebitda:24.87,dividend_yield_pct:1.59},
  {id:464,company_id:"SBIN",year:2020,market_cap_crore:1692341.99,enterprise_value_crore:1901297.81,pe_ratio:47.04,pb_ratio:2.29,ev_ebitda:20.41,dividend_yield_pct:3.65},
  {id:465,company_id:"SBIN",year:2021,market_cap_crore:1705155.98,enterprise_value_crore:1837361.16,pe_ratio:43.56,pb_ratio:13.01,ev_ebitda:27.95,dividend_yield_pct:0.45},
  {id:466,company_id:"SBIN",year:2022,market_cap_crore:2187008.32,enterprise_value_crore:2696201.57,pe_ratio:62.26,pb_ratio:7.26,ev_ebitda:31.51,dividend_yield_pct:2.15},
  {id:467,company_id:"SBIN",year:2023,market_cap_crore:2664457.97,enterprise_value_crore:3336018.79,pe_ratio:72.12,pb_ratio:7.09,ev_ebitda:35.08,dividend_yield_pct:0.46},
  {id:468,company_id:"SBIN",year:2024,market_cap_crore:2400436.05,enterprise_value_crore:2686824.35,pe_ratio:54.93,pb_ratio:2.72,ev_ebitda:21.53,dividend_yield_pct:0.42},
  {id:487,company_id:"SUNPHARMA",year:2019,market_cap_crore:758612.89,enterprise_value_crore:960774.91,pe_ratio:74.3,pb_ratio:10.71,ev_ebitda:27.29,dividend_yield_pct:2.39},
  {id:488,company_id:"SUNPHARMA",year:2020,market_cap_crore:714309.02,enterprise_value_crore:678202.02,pe_ratio:42.97,pb_ratio:2.81,ev_ebitda:25.19,dividend_yield_pct:2.91},
  {id:489,company_id:"SUNPHARMA",year:2021,market_cap_crore:794888.64,enterprise_value_crore:726981.85,pe_ratio:12.16,pb_ratio:2.14,ev_ebitda:10.38,dividend_yield_pct:4.45},
  {id:490,company_id:"SUNPHARMA",year:2022,market_cap_crore:812572.94,enterprise_value_crore:826215.51,pe_ratio:11.76,pb_ratio:9.71,ev_ebitda:27.83,dividend_yield_pct:0.79},
  {id:491,company_id:"SUNPHARMA",year:2023,market_cap_crore:1064162.39,enterprise_value_crore:1298488.21,pe_ratio:24.58,pb_ratio:7.54,ev_ebitda:21.04,dividend_yield_pct:1.57},
  {id:492,company_id:"SUNPHARMA",year:2024,market_cap_crore:1339586.09,enterprise_value_crore:1264175.16,pe_ratio:37.9,pb_ratio:6.71,ev_ebitda:21.41,dividend_yield_pct:3.88},
  {id:511,company_id:"TATASTEEL",year:2019,market_cap_crore:363770.91,enterprise_value_crore:433930.41,pe_ratio:55.54,pb_ratio:7.39,ev_ebitda:6.84,dividend_yield_pct:4.32},
  {id:512,company_id:"TATASTEEL",year:2020,market_cap_crore:339775.94,enterprise_value_crore:396643.74,pe_ratio:73.73,pb_ratio:10.62,ev_ebitda:12.63,dividend_yield_pct:1.42},
  {id:513,company_id:"TATASTEEL",year:2021,market_cap_crore:293941.16,enterprise_value_crore:336592.99,pe_ratio:52.14,pb_ratio:11.02,ev_ebitda:5.38,dividend_yield_pct:3.68},
  {id:514,company_id:"TATASTEEL",year:2022,market_cap_crore:358418.76,enterprise_value_crore:342775.45,pe_ratio:33.03,pb_ratio:9.76,ev_ebitda:22.35,dividend_yield_pct:0.52},
  {id:515,company_id:"TATASTEEL",year:2023,market_cap_crore:320309.06,enterprise_value_crore:388401.17,pe_ratio:19.23,pb_ratio:3,ev_ebitda:34.08,dividend_yield_pct:2.75},
  {id:516,company_id:"TATASTEEL",year:2024,market_cap_crore:369110.65,enterprise_value_crore:402972.23,pe_ratio:48.97,pb_ratio:9.23,ev_ebitda:38.87,dividend_yield_pct:1},
  {id:517,company_id:"TCS",year:2019,market_cap_crore:286225.25,enterprise_value_crore:332959.97,pe_ratio:47.53,pb_ratio:2.11,ev_ebitda:17.76,dividend_yield_pct:0.8},
  {id:518,company_id:"TCS",year:2020,market_cap_crore:290730.69,enterprise_value_crore:372282.29,pe_ratio:57.2,pb_ratio:0.61,ev_ebitda:13.84,dividend_yield_pct:0.05},
  {id:519,company_id:"TCS",year:2021,market_cap_crore:351038.19,enterprise_value_crore:381848.36,pe_ratio:79.57,pb_ratio:11.14,ev_ebitda:23.13,dividend_yield_pct:3.62},
  {id:520,company_id:"TCS",year:2022,market_cap_crore:422088.96,enterprise_value_crore:421038.16,pe_ratio:46.18,pb_ratio:8.56,ev_ebitda:20.79,dividend_yield_pct:0.81},
  {id:521,company_id:"TCS",year:2023,market_cap_crore:405916.42,enterprise_value_crore:410957.48,pe_ratio:8.74,pb_ratio:13.8,ev_ebitda:29.01,dividend_yield_pct:3.1},
  {id:522,company_id:"TCS",year:2024,market_cap_crore:461188.15,enterprise_value_crore:542230.13,pe_ratio:78.69,pb_ratio:6.08,ev_ebitda:29.94,dividend_yield_pct:1.62},
  {id:533,company_id:"TITAN",year:2023,market_cap_crore:1862221.59,enterprise_value_crore:2367970.55,pe_ratio:28.61,pb_ratio:3.98,ev_ebitda:23.08,dividend_yield_pct:2.29},
  {id:534,company_id:"TITAN",year:2024,market_cap_crore:1793769.72,enterprise_value_crore:2116401.21,pe_ratio:10.13,pb_ratio:10.51,ev_ebitda:21,dividend_yield_pct:3.1}
];

export const RAW_FINANCIAL_RATIOS_DATA = [
  {id:1,company_id:"ABB",year:"Dec 2012",net_profit_margin_pct:8.77,operating_profit_margin_pct:12,return_on_equity_pct:22.41,debt_to_equity:0,interest_coverage:null,asset_turnover:1.8225,free_cash_flow_cr:42,capex_cr:59,earnings_per_share:68,book_value_per_share:3.081,dividend_payout_ratio_pct:25,total_debt_cr:0,cash_from_operations_cr:101},
  {id:22,company_id:"ABB",year:"Mar 2024",net_profit_margin_pct:20.53,operating_profit_margin_pct:25,return_on_equity_pct:32.47,debt_to_equity:0.0224,interest_coverage:141.75,asset_turnover:1.1263,free_cash_flow_cr:797,capex_cr:416,earnings_per_share:565,book_value_per_share:17.6143,dividend_payout_ratio_pct:73,total_debt_cr:83,cash_from_operations_cr:1213},
  {id:34,company_id:"ADANIENSOL",year:"Mar 2024",net_profit_margin_pct:7.2,operating_profit_margin_pct:30,return_on_equity_pct:9.46,debt_to_equity:2.9325,interest_coverage:2.2848,asset_turnover:0.2837,free_cash_flow_cr:1095,capex_cr:4943,earnings_per_share:10,book_value_per_share:1.1337,dividend_payout_ratio_pct:0,total_debt_cr:37070,cash_from_operations_cr:6038},
  {id:46,company_id:"ADANIENT",year:"Mar 2024",net_profit_margin_pct:3.46,operating_profit_margin_pct:12,return_on_equity_pct:8.53,debt_to_equity:1.6714,interest_coverage:2.7493,asset_turnover:0.6004,free_cash_flow_cr:-8455,capex_cr:18767,earnings_per_share:28,book_value_per_share:34.2772,dividend_payout_ratio_pct:5,total_debt_cr:65310,cash_from_operations_cr:10312},
  {id:54,company_id:"ADANIGREEN",year:"Mar 2024",net_profit_margin_pct:13.67,operating_profit_margin_pct:79,return_on_equity_pct:12.81,debt_to_equity:6.5953,interest_coverage:1.7139,asset_turnover:0.1047,free_cash_flow_cr:-13347,capex_cr:21060,earnings_per_share:7,book_value_per_share:0.6208,dividend_payout_ratio_pct:0,total_debt_cr:64858,cash_from_operations_cr:7713},
  {id:66,company_id:"ADANIPORTS",year:"Mar 2024",net_profit_margin_pct:30.34,operating_profit_margin_pct:58,return_on_equity_pct:15.35,debt_to_equity:0.9373,interest_coverage:5.9495,asset_turnover:0.2283,free_cash_flow_cr:8250,capex_cr:6768,earnings_per_share:38,book_value_per_share:12.2171,dividend_payout_ratio_pct:16,total_debt_cr:49470,cash_from_operations_cr:15018},
  {id:90,company_id:"ADANIPOWER",year:"Mar 2024",net_profit_margin_pct:41.37,operating_profit_margin_pct:36,return_on_equity_pct:48.28,debt_to_equity:0.8023,interest_coverage:8.2972,asset_turnover:0.5472,free_cash_flow_cr:17651,capex_cr:3481,earnings_per_share:54,book_value_per_share:1.1186,dividend_payout_ratio_pct:0,total_debt_cr:34616,cash_from_operations_cr:14170},
  {id:101,company_id:"AMBUJACEM",year:"Mar 2024",net_profit_margin_pct:14.29,operating_profit_margin_pct:19,return_on_equity_pct:11.43,debt_to_equity:0.0169,interest_coverage:28.2645,asset_turnover:0.5081,free_cash_flow_cr:-3295,capex_cr:8941,earnings_per_share:16,book_value_per_share:9.4218,dividend_payout_ratio_pct:12,total_debt_cr:699,cash_from_operations_cr:5646},
  {id:113,company_id:"APOLLOHOSP",year:"Mar 2024",net_profit_margin_pct:4.91,operating_profit_margin_pct:13,return_on_equity_pct:13.48,debt_to_equity:0.7689,interest_coverage:5.5657,asset_turnover:1.1384,free_cash_flow_cr:383,capex_cr:1537,earnings_per_share:63,book_value_per_share:9.6333,dividend_payout_ratio_pct:26,total_debt_cr:5333,cash_from_operations_cr:1920},
  {id:137,company_id:"ASIANPAINT",year:"Mar 2024",net_profit_margin_pct:15.66,operating_profit_margin_pct:21,return_on_equity_pct:29.68,debt_to_equity:0.1321,interest_coverage:41.0049,asset_turnover:1.1871,free_cash_flow_cr:3556,capex_cr:2548,earnings_per_share:57,book_value_per_share:19.5083,dividend_payout_ratio_pct:58,total_debt_cr:2474,cash_from_operations_cr:6104},
  {id:161,company_id:"BAJAJ-AUTO",year:"Mar 2024",net_profit_margin_pct:17.18,operating_profit_margin_pct:20,return_on_equity_pct:26.61,debt_to_equity:0.066,interest_coverage:174.4167,asset_turnover:1.1405,free_cash_flow_cr:6486,capex_cr:72,earnings_per_share:276,book_value_per_share:10.3806,dividend_payout_ratio_pct:29,total_debt_cr:1912,cash_from_operations_cr:6558},
  {id:173,company_id:"AXISBANK",year:"Mar 2024",net_profit_margin_pct:22.73,operating_profit_margin_pct:11952,return_on_equity_pct:15.83,debt_to_equity:8.2491,interest_coverage:1.6912,asset_turnover:0.072,free_cash_flow_cr:-14556,capex_cr:9001,earnings_per_share:81,book_value_per_share:25.4494,dividend_payout_ratio_pct:1,total_debt_cr:1295302,cash_from_operations_cr:-5555},
  {id:185,company_id:"BAJAJFINSV",year:"Mar 2024",net_profit_margin_pct:14.13,operating_profit_margin_pct:37,return_on_equity_pct:25.85,debt_to_equity:4.7894,interest_coverage:2.1971,asset_turnover:0.2054,free_cash_flow_cr:-79634,capex_cr:10960,earnings_per_share:51,book_value_per_share:37.9421,dividend_payout_ratio_pct:2,total_debt_cr:288933,cash_from_operations_cr:-68674},
  {id:197,company_id:"BAJAJHLDNG",year:"Mar 2024",net_profit_margin_pct:432.73,operating_profit_margin_pct:92,return_on_equity_pct:13.58,debt_to_equity:0.0012,interest_coverage:3764.5,asset_turnover:0.0261,free_cash_flow_cr:1469,capex_cr:472,earnings_per_share:653,book_value_per_share:48.8712,dividend_payout_ratio_pct:20,total_debt_cr:63,cash_from_operations_cr:1941},
  {id:207,company_id:"BAJFINANCE",year:"Mar 2024",net_profit_margin_pct:26.29,operating_profit_margin_pct:19987,return_on_equity_pct:18.84,debt_to_equity:3.8248,interest_coverage:2689.1667,asset_turnover:0.1463,free_cash_flow_cr:-79931,capex_cr:7171,earnings_per_share:233,book_value_per_share:61.8516,dividend_payout_ratio_pct:15,total_debt_cr:293346,cash_from_operations_cr:-72760},
  {id:219,company_id:"BANKBARODA",year:"Mar 2024",net_profit_margin_pct:15.94,operating_profit_margin_pct:4102,return_on_equity_pct:15.76,debt_to_equity:12.1437,interest_coverage:1.8967,asset_turnover:0.0715,free_cash_flow_cr:-7559,capex_cr:1285,earnings_per_share:36,book_value_per_share:11.5553,dividend_payout_ratio_pct:21,total_debt_cr:1453761,cash_from_operations_cr:-6274},
  {id:231,company_id:"BHARTIARTL",year:"Mar 2024",net_profit_margin_pct:5.71,operating_profit_margin_pct:52,return_on_equity_pct:10.36,debt_to_equity:2.6095,interest_coverage:3.3055,asset_turnover:0.3393,free_cash_flow_cr:27809,capex_cr:51089,earnings_per_share:13,book_value_per_share:2.8717,dividend_payout_ratio_pct:62,total_debt_cr:215592,cash_from_operations_cr:78898},
  {id:243,company_id:"BEL",year:"Mar 2024",net_profit_margin_pct:19.66,operating_profit_margin_pct:25,return_on_equity_pct:24.4,debt_to_equity:0.001,interest_coverage:476.75,asset_turnover:1.258,free_cash_flow_cr:-1265,capex_cr:5924,earnings_per_share:5,book_value_per_share:0.7636,dividend_payout_ratio_pct:40,total_debt_cr:43,cash_from_operations_cr:4659},
  {id:255,company_id:"BHEL",year:"Mar 2024",net_profit_margin_pct:1.18,operating_profit_margin_pct:3,return_on_equity_pct:1.15,debt_to_equity:0.3624,interest_coverage:1.593,asset_turnover:0.3996,free_cash_flow_cr:-2382,capex_cr:1331,earnings_per_share:1,book_value_per_share:3.5112,dividend_payout_ratio_pct:31,total_debt_cr:8856,cash_from_operations_cr:-3713},
  {id:267,company_id:"BOSCHLTD",year:"Mar 2024",net_profit_margin_pct:14.89,operating_profit_margin_pct:13,return_on_equity_pct:20.64,debt_to_equity:0.0032,interest_coverage:71.7843,asset_turnover:0.9638,free_cash_flow_cr:1536,capex_cr:283,earnings_per_share:844,book_value_per_share:40.2133,dividend_payout_ratio_pct:44,total_debt_cr:39,cash_from_operations_cr:1253},
  {id:279,company_id:"BPCL",year:"Mar 2024",net_profit_margin_pct:5.99,operating_profit_margin_pct:10,return_on_equity_pct:35.51,debt_to_equity:0.7219,interest_coverage:11.3555,asset_turnover:2.2137,free_cash_flow_cr:25415,capex_cr:10521,earnings_per_share:62,book_value_per_share:3.541,dividend_payout_ratio_pct:33,total_debt_cr:54599,cash_from_operations_cr:35936},
  {id:291,company_id:"BRITANNIA",year:"Mar 2024",net_profit_margin_pct:12.73,operating_profit_margin_pct:19,return_on_equity_pct:54.15,debt_to_equity:0.524,interest_coverage:20.5976,asset_turnover:1.8484,free_cash_flow_cr:3050,capex_cr:477,earnings_per_share:89,book_value_per_share:16.4208,dividend_payout_ratio_pct:83,total_debt_cr:2065,cash_from_operations_cr:2573},
  {id:303,company_id:"CANBK",year:"Mar 2024",net_profit_margin_pct:13.94,operating_profit_margin_pct:-7745,return_on_equity_pct:16.72,debt_to_equity:14.8674,interest_coverage:1.6107,asset_turnover:0.072,free_cash_flow_cr:13296,capex_cr:1750,earnings_per_share:17,book_value_per_share:5.079,dividend_payout_ratio_pct:19,total_debt_cr:1369780,cash_from_operations_cr:15046},
  {id:315,company_id:"CHOLAFIN",year:"Mar 2024",net_profit_margin_pct:17.85,operating_profit_margin_pct:4548,return_on_equity_pct:17.46,debt_to_equity:6.8634,interest_coverage:21.2118,asset_turnover:0.1223,free_cash_flow_cr:-38538,capex_cr:2855,earnings_per_share:41,book_value_per_share:11.6625,dividend_payout_ratio_pct:5,total_debt_cr:134475,cash_from_operations_cr:-35683},
  {id:327,company_id:"CIPLA",year:"Mar 2024",net_profit_margin_pct:16.12,operating_profit_margin_pct:6291,return_on_equity_pct:15.55,debt_to_equity:0.0209,interest_coverage:35.3388,asset_turnover:0.7922,free_cash_flow_cr:1152,capex_cr:2982,earnings_per_share:51,book_value_per_share:16.5876,dividend_payout_ratio_pct:25,total_debt_cr:559,cash_from_operations_cr:4134},
  {id:339,company_id:"COALINDIA",year:"Mar 2024",net_profit_margin_pct:26.26,operating_profit_margin_pct:47971,return_on_equity_pct:45.17,debt_to_equity:0.0788,interest_coverage:11.2418,asset_turnover:0.6019,free_cash_flow_cr:13617,capex_cr:4486,earnings_per_share:61,book_value_per_share:1.3424,dividend_payout_ratio_pct:42,total_debt_cr:6523,cash_from_operations_cr:18103},
  {id:351,company_id:"DABUR",year:"Mar 2024",net_profit_margin_pct:14.6,operating_profit_margin_pct:19,return_on_equity_pct:18.36,debt_to_equity:0.1384,interest_coverage:23.2419,asset_turnover:0.8206,free_cash_flow_cr:1042,capex_cr:971,earnings_per_share:10,book_value_per_share:5.574,dividend_payout_ratio_pct:53,total_debt_cr:1365,cash_from_operations_cr:2013},
  {id:363,company_id:"DIVISLAB",year:"Mar 2024",net_profit_margin_pct:20.4,operating_profit_margin_pct:28,return_on_equity_pct:11.79,debt_to_equity:0.0002,interest_coverage:636.25,asset_turnover:0.5074,free_cash_flow_cr:992,capex_cr:269,earnings_per_share:60,book_value_per_share:25.6057,dividend_payout_ratio_pct:50,total_debt_cr:3,cash_from_operations_cr:1261},
  {id:375,company_id:"DLF",year:"Mar 2024",net_profit_margin_pct:42.38,operating_profit_margin_pct:33,return_on_equity_pct:6.91,debt_to_equity:0.1226,interest_coverage:7.4579,asset_turnover:0.1088,free_cash_flow_cr:1010,capex_cr:1529,earnings_per_share:11,book_value_per_share:7.9659,dividend_payout_ratio_pct:45,total_debt_cr:4834,cash_from_operations_cr:2539},
  {id:387,company_id:"DMART",year:"Mar 2024",net_profit_margin_pct:4.99,operating_profit_margin_pct:8,return_on_equity_pct:13.56,debt_to_equity:0.0317,interest_coverage:73.2931,asset_turnover:2.3989,free_cash_flow_cr:278,capex_cr:2468,earnings_per_share:39,book_value_per_share:2.8722,dividend_payout_ratio_pct:0,total_debt_cr:592,cash_from_operations_cr:2746},
  {id:399,company_id:"DRREDDY",year:"Mar 2024",net_profit_margin_pct:19.91,operating_profit_margin_pct:28,return_on_equity_pct:19.74,debt_to_equity:0.0709,interest_coverage:51.7076,asset_turnover:0.7223,free_cash_flow_cr:509,capex_cr:4034,earnings_per_share:67,book_value_per_share:34.041,dividend_payout_ratio_pct:12,total_debt_cr:2002,cash_from_operations_cr:4543},
  {id:411,company_id:"EICHERMOT",year:"Mar 2024",net_profit_margin_pct:24.2,operating_profit_margin_pct:26,return_on_equity_pct:22.17,debt_to_equity:0.0232,interest_coverage:114.7059,asset_turnover:0.7154,free_cash_flow_cr:890,capex_cr:2834,earnings_per_share:146,book_value_per_share:66.8333,dividend_payout_ratio_pct:35,total_debt_cr:419,cash_from_operations_cr:3724},
  {id:423,company_id:"GAIL",year:"Mar 2024",net_profit_margin_pct:7.43,operating_profit_margin_pct:11,return_on_equity_pct:12.86,debt_to_equity:0.283,interest_coverage:23.6245,asset_turnover:1.0681,free_cash_flow_cr:4360,capex_cr:8226,earnings_per_share:15,book_value_per_share:1.1711,dividend_payout_ratio_pct:37,total_debt_cr:21794,cash_from_operations_cr:12586},
  {id:435,company_id:"GODREJCP",year:"Mar 2024",net_profit_margin_pct:-3.98,operating_profit_margin_pct:21,return_on_equity_pct:-4.45,debt_to_equity:0.2558,interest_coverage:2.4129,asset_turnover:0.7664,free_cash_flow_cr:-1365,capex_cr:3435,earnings_per_share:-5,book_value_per_share:12.351,dividend_payout_ratio_pct:null,total_debt_cr:3222,cash_from_operations_cr:2070},
  {id:447,company_id:"GRASIM",year:"Mar 2024",net_profit_margin_pct:7.58,operating_profit_margin_pct:21,return_on_equity_pct:11.2,debt_to_equity:1.5471,interest_coverage:3.0158,asset_turnover:0.3178,free_cash_flow_cr:-33833,capex_cr:23114,earnings_per_share:85,book_value_per_share:66.6564,dividend_payout_ratio_pct:12,total_debt_cr:137155,cash_from_operations_cr:-10719},
  {id:455,company_id:"HAL",year:"Mar 2024",net_profit_margin_pct:25,operating_profit_margin_pct:32,return_on_equity_pct:28.16,debt_to_equity:0.005,interest_coverage:270.8837,asset_turnover:0.6751,free_cash_flow_cr:1814,capex_cr:6412,earnings_per_share:114,book_value_per_share:3.98,dividend_payout_ratio_pct:31,total_debt_cr:123,cash_from_operations_cr:8226},
  {id:467,company_id:"HAVELLS",year:"Mar 2024",net_profit_margin_pct:6.84,operating_profit_margin_pct:10,return_on_equity_pct:17.07,debt_to_equity:0.0407,interest_coverage:25.3571,asset_turnover:1.4952,free_cash_flow_cr:335,capex_cr:1618,earnings_per_share:20,book_value_per_share:11.8206,dividend_payout_ratio_pct:44,total_debt_cr:303,cash_from_operations_cr:1953},
  {id:478,company_id:"HCLTECH",year:"Mar 2024",net_profit_margin_pct:14.29,operating_profit_margin_pct:22,return_on_equity_pct:23.01,debt_to_equity:0.0844,interest_coverage:46.4611,asset_turnover:1.1102,free_cash_flow_cr:15840,capex_cr:6608,earnings_per_share:58,book_value_per_share:12.5715,dividend_payout_ratio_pct:90,total_debt_cr:5758,cash_from_operations_cr:22448},
  {id:490,company_id:"HDFCBANK",year:"Mar 2024",net_profit_margin_pct:23.07,operating_profit_margin_pct:-44685,return_on_equity_pct:14.34,debt_to_equity:6.8088,interest_coverage:1.4008,asset_turnover:0.0704,free_cash_flow_cr:35669,capex_cr:16600,earnings_per_share:84,book_value_per_share:60.0521,dividend_payout_ratio_pct:23,total_debt_cr:3107503,cash_from_operations_cr:19069},
  {id:502,company_id:"HDFCLIFE",year:"Mar 2024",net_profit_margin_pct:1.55,operating_profit_margin_pct:531,return_on_equity_pct:10.73,debt_to_equity:0.0648,interest_coverage:192.2895,asset_turnover:0.3353,free_cash_flow_cr:-2893,capex_cr:13614,earnings_per_share:7,book_value_per_share:0.6818,dividend_payout_ratio_pct:27,total_debt_cr:950,cash_from_operations_cr:10721},
  {id:513,company_id:"HEROMOTOCO",year:"Mar 2024",net_profit_margin_pct:9.9,operating_profit_margin_pct:5235,return_on_equity_pct:21.14,debt_to_equity:0.0342,interest_coverage:47.2685,asset_turnover:1.4449,free_cash_flow_cr:3095,capex_cr:1828,earnings_per_share:187,book_value_per_share:44.2475,dividend_payout_ratio_pct:75,total_debt_cr:606,cash_from_operations_cr:4923},
  {id:525,company_id:"HINDALCO",year:"Mar 2024",net_profit_margin_pct:4.7,operating_profit_margin_pct:23872,return_on_equity_pct:9.57,debt_to_equity:0.5309,interest_coverage:126.4654,asset_turnover:0.936,free_cash_flow_cr:9789,capex_cr:14267,earnings_per_share:45,book_value_per_share:47.8135,dividend_payout_ratio_pct:8,total_debt_cr:56356,cash_from_operations_cr:24056},
  {id:537,company_id:"HINDUNILVR",year:"Mar 2024",net_profit_margin_pct:16.61,operating_profit_margin_pct:14659,return_on_equity_pct:20.07,debt_to_equity:0.029,interest_coverage:57.847,asset_turnover:0.7886,free_cash_flow_cr:10145,capex_cr:5324,earnings_per_share:44,book_value_per_share:21.7949,dividend_payout_ratio_pct:96,total_debt_cr:1484,cash_from_operations_cr:15469},
  {id:549,company_id:"ICICIBANK",year:"Mar 2024",net_profit_margin_pct:28.89,operating_profit_margin_pct:-14152,return_on_equity_pct:17.99,debt_to_equity:6.4456,interest_coverage:1.3009,asset_turnover:0.0675,free_cash_flow_cr:12547,capex_cr:144737,earnings_per_share:63,book_value_per_share:18.2309,dividend_payout_ratio_pct:16,total_debt_cr:1651008,cash_from_operations_cr:157284},
  {id:597,company_id:"INFY",year:"Mar 2024",net_profit_margin_pct:17.08,operating_profit_margin_pct:24,return_on_equity_pct:29.79,debt_to_equity:0.0949,interest_coverage:87.5234,asset_turnover:1.1298,free_cash_flow_cr:20117,capex_cr:5093,earnings_per_share:63,book_value_per_share:4.2548,dividend_payout_ratio_pct:70,total_debt_cr:8359,cash_from_operations_cr:25210},
  {id:609,company_id:"IOC",year:"Mar 2024",net_profit_margin_pct:5.56,operating_profit_margin_pct:10,return_on_equity_pct:23.53,debt_to_equity:0.7231,interest_coverage:10.2823,asset_turnover:1.6084,free_cash_flow_cr:39635,capex_cr:31464,earnings_per_share:30,book_value_per_share:1.3318,dividend_payout_ratio_pct:40,total_debt_cr:132628,cash_from_operations_cr:71099},
  {id:640,company_id:"ITC",year:"Mar 2024",net_profit_margin_pct:29.28,operating_profit_margin_pct:37,return_on_equity_pct:27.85,debt_to_equity:0.0041,interest_coverage:362.9625,asset_turnover:0.7723,free_cash_flow_cr:18742,capex_cr:1563,earnings_per_share:16,book_value_per_share:5.9701,dividend_payout_ratio_pct:84,total_debt_cr:303,cash_from_operations_cr:17179},
  {id:666,company_id:"JSWENERGY",year:"Mar 2024",net_profit_margin_pct:15.02,operating_profit_margin_pct:47,return_on_equity_pct:8.28,debt_to_equity:1.5156,interest_coverage:2.8514,asset_turnover:0.1988,free_cash_flow_cr:-1963,capex_cr:8197,earnings_per_share:10,book_value_per_share:1.2695,dividend_payout_ratio_pct:19,total_debt_cr:31573,cash_from_operations_cr:6234},
  {id:678,company_id:"JSWSTEEL",year:"Mar 2024",net_profit_margin_pct:5.13,operating_profit_margin_pct:16,return_on_equity_pct:11.55,debt_to_equity:1.1328,interest_coverage:3.6591,asset_turnover:0.7679,free_cash_flow_cr:-2389,capex_cr:14467,earnings_per_share:36,book_value_per_share:25.4652,dividend_payout_ratio_pct:25,total_debt_cr:87984,cash_from_operations_cr:12078},
  {id:690,company_id:"KOTAKBANK",year:"Mar 2024",net_profit_margin_pct:32.39,operating_profit_margin_pct:-13382,return_on_equity_pct:14.01,debt_to_equity:4.0037,interest_coverage:1.2364,asset_turnover:0.0733,free_cash_flow_cr:6766,capex_cr:8919,earnings_per_share:92,book_value_per_share:13.0757,dividend_payout_ratio_pct:2,total_debt_cr:520374,cash_from_operations_cr:15685},
  {id:696,company_id:"LICI",year:"Mar 2024",net_profit_margin_pct:4.84,operating_profit_margin_pct:4,return_on_equity_pct:49.45,debt_to_equity:0,interest_coverage:371.9375,asset_turnover:0.1591,free_cash_flow_cr:853,capex_cr:25269,earnings_per_share:66,book_value_per_share:1.3083,dividend_payout_ratio_pct:15,total_debt_cr:0,cash_from_operations_cr:26122},
  {id:717,company_id:"LT",year:"Mar 2024",net_profit_margin_pct:7.03,operating_profit_margin_pct:14,return_on_equity_pct:17.67,debt_to_equity:0.1035,interest_coverage:3.5442,asset_turnover:8.0276,free_cash_flow_cr:20445,capex_cr:2179,earnings_per_share:95,book_value_per_share:66.7267,dividend_payout_ratio_pct:36,total_debt_cr:2071,cash_from_operations_cr:18266},
  {id:729,company_id:"LTIM",year:"Mar 2024",net_profit_margin_pct:12.91,operating_profit_margin_pct:18,return_on_equity_pct:22.9,debt_to_equity:0.1035,interest_coverage:31.9324,asset_turnover:1.2895,free_cash_flow_cr:1752,capex_cr:3918,earnings_per_share:155,book_value_per_share:66.7267,dividend_payout_ratio_pct:42,total_debt_cr:2071,cash_from_operations_cr:5670},
  {id:741,company_id:"M&M",year:"Mar 2024",net_profit_margin_pct:8.82,operating_profit_margin_pct:18,return_on_equity_pct:18.54,debt_to_equity:1.6414,interest_coverage:3.7647,asset_turnover:0.5925,free_cash_flow_cr:-11245,capex_cr:5615,earnings_per_share:91,book_value_per_share:11.8833,dividend_payout_ratio_pct:21,total_debt_cr:108647,cash_from_operations_cr:-5630},
  {id:753,company_id:"MARUTI",year:"Mar 2024",net_profit_margin_pct:9.51,operating_profit_margin_pct:13,return_on_equity_pct:15.75,debt_to_equity:0.0014,interest_coverage:117.9072,asset_turnover:1.2303,free_cash_flow_cr:4936,capex_cr:11865,earnings_per_share:429,book_value_per_share:54.5452,dividend_payout_ratio_pct:29,total_debt_cr:119,cash_from_operations_cr:16801},
  {id:765,company_id:"MOTHERSON",year:"Mar 2024",net_profit_margin_pct:3.06,operating_profit_margin_pct:9,return_on_equity_pct:11.55,debt_to_equity:0.7617,interest_coverage:5.2247,asset_turnover:1.1724,free_cash_flow_cr:925,capex_cr:6644,earnings_per_share:4,book_value_per_share:3.8577,dividend_payout_ratio_pct:20,total_debt_cr:19922,cash_from_operations_cr:7569},
  {id:777,company_id:"NAUKRI",year:"Mar 2024",net_profit_margin_pct:23.46,operating_profit_margin_pct:28,return_on_equity_pct:1.97,debt_to_equity:0.0081,interest_coverage:28.9714,asset_turnover:0.0703,free_cash_flow_cr:-150,capex_cr:852,earnings_per_share:44,book_value_per_share:23.4589,dividend_payout_ratio_pct:49,total_debt_cr:246,cash_from_operations_cr:702},
  {id:789,company_id:"NESTLEIND",year:"Mar 2024",net_profit_margin_pct:16.12,operating_profit_margin_pct:24,return_on_equity_pct:117.75,debt_to_equity:0.1033,interest_coverage:41.1862,asset_turnover:2.3182,free_cash_flow_cr:2938,capex_cr:1237,earnings_per_share:41,book_value_per_share:3.4792,dividend_payout_ratio_pct:79,total_debt_cr:345,cash_from_operations_cr:4175},
  {id:801,company_id:"NHPC",year:"Mar 2024",net_profit_margin_pct:41.82,operating_profit_margin_pct:50,return_on_equity_pct:10.41,debt_to_equity:0.8413,interest_coverage:11.2434,asset_turnover:0.1032,free_cash_flow_cr:970,capex_cr:5968,earnings_per_share:4,book_value_per_share:0.3853,dividend_payout_ratio_pct:53,total_debt_cr:32561,cash_from_operations_cr:6938},
  {id:813,company_id:"NTPC",year:"Mar 2024",net_profit_margin_pct:11.95,operating_profit_margin_pct:29,return_on_equity_pct:13.27,debt_to_equity:1.4755,interest_coverage:4.605,asset_turnover:0.3724,free_cash_flow_cr:8644,capex_cr:32141,earnings_per_share:21,book_value_per_share:1.6573,dividend_payout_ratio_pct:36,total_debt_cr:237131,cash_from_operations_cr:40785},
  {id:825,company_id:"ONGC",year:"Mar 2024",net_profit_margin_pct:9.66,operating_profit_margin_pct:17,return_on_equity_pct:16.94,debt_to_equity:0.4544,interest_coverage:11.3613,asset_turnover:0.8332,free_cash_flow_cr:42060,capex_cr:57203,earnings_per_share:39,book_value_per_share:5.3588,dividend_payout_ratio_pct:31,total_debt_cr:153181,cash_from_operations_cr:99263},
  {id:837,company_id:"PFC",year:"Mar 2024",net_profit_margin_pct:28.92,operating_profit_margin_pct:37,return_on_equity_pct:26.16,debt_to_equity:8.5219,interest_coverage:0.5804,asset_turnover:0.0881,free_cash_flow_cr:-101229,capex_cr:3409,earnings_per_share:60,book_value_per_share:3.0651,dividend_payout_ratio_pct:23,total_debt_cr:861961,cash_from_operations_cr:-97820},
  {id:849,company_id:"PIDILITIND",year:"Mar 2024",net_profit_margin_pct:14.11,operating_profit_margin_pct:22,return_on_equity_pct:20.78,debt_to_equity:0.0454,interest_coverage:54.3333,asset_turnover:1.0254,free_cash_flow_cr:955,capex_cr:1769,earnings_per_share:34,book_value_per_share:16.4843,dividend_payout_ratio_pct:47,total_debt_cr:382,cash_from_operations_cr:2724},
  {id:905,company_id:"PNB",year:"Mar 2024",net_profit_margin_pct:8.4,operating_profit_margin_pct:null,return_on_equity_pct:61.32,debt_to_equity:3.6843,interest_coverage:null,asset_turnover:1.507,free_cash_flow_cr:-29445,capex_cr:1506,earnings_per_share:8,book_value_per_share:5.7435,dividend_payout_ratio_pct:18,total_debt_cr:55017,cash_from_operations_cr:-27939},
  {id:932,company_id:"POWERGRID",year:"Mar 2024",net_profit_margin_pct:33.97,operating_profit_margin_pct:87,return_on_equity_pct:17.87,debt_to_equity:1.4173,interest_coverage:4.603,asset_turnover:0.1828,free_cash_flow_cr:24176,capex_cr:13114,earnings_per_share:17,book_value_per_share:0.937,dividend_payout_ratio_pct:67,total_debt_cr:123516,cash_from_operations_cr:37290},
  {id:945,company_id:"RECLTD",year:"Mar 2024",net_profit_margin_pct:29.77,operating_profit_margin_pct:101,return_on_equity_pct:20.4,debt_to_equity:6.4249,interest_coverage:1.6005,asset_turnover:0.0867,free_cash_flow_cr:-59554,capex_cr:1831,earnings_per_share:54,book_value_per_share:2.6339,dividend_payout_ratio_pct:30,total_debt_cr:445568,cash_from_operations_cr:-57723},
  {id:957,company_id:"RELIANCE",year:"Mar 2024",net_profit_margin_pct:8.79,operating_profit_margin_pct:18,return_on_equity_pct:9.96,debt_to_equity:0.5785,interest_coverage:7.7289,asset_turnover:0.5123,free_cash_flow_cr:45207,capex_cr:113581,earnings_per_share:51,book_value_per_share:11.7275,dividend_payout_ratio_pct:10,total_debt_cr:458991,cash_from_operations_cr:158788},
  {id:969,company_id:"SBILIFE",year:"Mar 2024",net_profit_margin_pct:1.43,operating_profit_margin_pct:0,return_on_equity_pct:12.7,debt_to_equity:0,interest_coverage:240.3333,asset_turnover:0.3314,free_cash_flow_cr:-2099,capex_cr:31221,earnings_per_share:19,book_value_per_share:1.4893,dividend_payout_ratio_pct:14,total_debt_cr:0,cash_from_operations_cr:29122},
  {id:980,company_id:"SHREECEM",year:"Mar 2024",net_profit_margin_pct:8.45,operating_profit_margin_pct:22,return_on_equity_pct:8.37,debt_to_equity:0.08,interest_coverage:19.8256,asset_turnover:0.7349,free_cash_flow_cr:1929,capex_cr:1418,earnings_per_share:480,book_value_per_share:57.5083,dividend_payout_ratio_pct:16,total_debt_cr:1656,cash_from_operations_cr:3347},
  {id:992,company_id:"SHRIRAMFIN",year:"Mar 2024",net_profit_margin_pct:20.33,operating_profit_margin_pct:29,return_on_equity_pct:15.12,debt_to_equity:3.994,interest_coverage:0.6767,asset_turnover:0.1466,free_cash_flow_cr:-31359,capex_cr:258,earnings_per_share:39,book_value_per_share:13.0178,dividend_payout_ratio_pct:23,total_debt_cr:195496,cash_from_operations_cr:-31101},
  {id:1004,company_id:"SIEMENS",year:"Sep 2024",net_profit_margin_pct:12.22,operating_profit_margin_pct:14,return_on_equity_pct:17.7,debt_to_equity:0.0182,interest_coverage:67.15,asset_turnover:0.8791,free_cash_flow_cr:1168,capex_cr:502,earnings_per_share:76,book_value_per_share:21.6296,dividend_payout_ratio_pct:16,total_debt_cr:279,cash_from_operations_cr:1670},
  {id:1016,company_id:"SUNPHARMA",year:"Mar 2024",net_profit_margin_pct:19.82,operating_profit_margin_pct:28,return_on_equity_pct:15.09,debt_to_equity:0.0514,interest_coverage:58.3319,asset_turnover:0.5685,free_cash_flow_cr:11372,capex_cr:763,earnings_per_share:40,book_value_per_share:26.5279,dividend_payout_ratio_pct:34,total_debt_cr:3274,cash_from_operations_cr:12135},
  {id:1028,company_id:"TATACONSUM",year:"Mar 2024",net_profit_margin_pct:7.99,operating_profit_margin_pct:15,return_on_equity_pct:7.57,debt_to_equity:0.2165,interest_coverage:25.3218,asset_turnover:0.5454,free_cash_flow_cr:26,capex_cr:1911,earnings_per_share:12,book_value_per_share:16.9021,dividend_payout_ratio_pct:64,total_debt_cr:3477,cash_from_operations_cr:1937},
  {id:1040,company_id:"TATAMOTORS",year:"Mar 2024",net_profit_margin_pct:7.26,operating_profit_margin_pct:14,return_on_equity_pct:37.46,debt_to_equity:1.2631,interest_coverage:6.5302,asset_turnover:1.1851,free_cash_flow_cr:45133,capex_cr:22782,earnings_per_share:94,book_value_per_share:11.0859,dividend_payout_ratio_pct:7,total_debt_cr:107262,cash_from_operations_cr:67915},
  {id:1052,company_id:"TATAPOWER",year:"Mar 2024",net_profit_margin_pct:6.97,operating_profit_margin_pct:17,return_on_equity_pct:13.23,debt_to_equity:1.6593,interest_coverage:3.0544,asset_turnover:0.4419,free_cash_flow_cr:3569,capex_cr:9027,earnings_per_share:12,book_value_per_share:10.1113,dividend_payout_ratio_pct:17,total_debt_cr:53689,cash_from_operations_cr:12596},
  {id:1064,company_id:"TATASTEEL",year:"Mar 2024",net_profit_margin_pct:-2.14,operating_profit_margin_pct:10,return_on_equity_pct:-5.33,debt_to_equity:0.9462,interest_coverage:2.1634,asset_turnover:0.8509,free_cash_flow_cr:6048,capex_cr:14253,earnings_per_share:-4,book_value_per_share:7.3805,dividend_payout_ratio_pct:-101,total_debt_cr:87082,cash_from_operations_cr:20301},
  {id:1076,company_id:"TCS",year:"Mar 2024",net_profit_margin_pct:19.14,operating_profit_margin_pct:27,return_on_equity_pct:50.94,debt_to_equity:0.0886,interest_coverage:87.0951,asset_turnover:1.6559,free_cash_flow_cr:50429,capex_cr:6091,earnings_per_share:127,book_value_per_share:24.997,dividend_payout_ratio_pct:58,total_debt_cr:8021,cash_from_operations_cr:44338},
  {id:1100,company_id:"TECHM",year:"Mar 2024",net_profit_margin_pct:4.61,operating_profit_margin_pct:9,return_on_equity_pct:8.99,debt_to_equity:0.0951,interest_coverage:13.8597,asset_turnover:1.205,free_cash_flow_cr:5058,capex_cr:1318,earnings_per_share:24,book_value_per_share:6.0474,dividend_payout_ratio_pct:150,total_debt_cr:2537,cash_from_operations_cr:6376},
  {id:1112,company_id:"TITAN",year:"Mar 2024",net_profit_margin_pct:6.84,operating_profit_margin_pct:10,return_on_equity_pct:37.22,debt_to_equity:1.6531,interest_coverage:9.412,asset_turnover:1.6193,free_cash_flow_cr:1506,capex_cr:189,earnings_per_share:39,book_value_per_share:10.5539,dividend_payout_ratio_pct:28,total_debt_cr:15528,cash_from_operations_cr:1695},
  {id:1124,company_id:"TORNTPHARM",year:"Mar 2024",net_profit_margin_pct:15.44,operating_profit_margin_pct:31,return_on_equity_pct:24.15,debt_to_equity:0.5866,interest_coverage:9.9266,asset_turnover:0.7396,free_cash_flow_cr:3106,capex_cr:160,earnings_per_share:49,book_value_per_share:4.0568,dividend_payout_ratio_pct:57,total_debt_cr:4022,cash_from_operations_cr:3266},
  {id:1136,company_id:"TRENT",year:"Mar 2024",net_profit_margin_pct:11.94,operating_profit_margin_pct:16,return_on_equity_pct:36.31,debt_to_equity:0.4309,interest_coverage:8.0435,asset_turnover:1.7279,free_cash_flow_cr:841,capex_cr:508,earnings_per_share:42,book_value_per_share:11.3,dividend_payout_ratio_pct:8,total_debt_cr:1753,cash_from_operations_cr:1349},
  {id:1148,company_id:"TVSMOTOR",year:"Mar 2024",net_profit_margin_pct:4.54,operating_profit_margin_pct:14,return_on_equity_pct:26.22,debt_to_equity:3.8334,interest_coverage:2.9077,asset_turnover:0.9315,free_cash_flow_cr:-2254,capex_cr:1001,earnings_per_share:36,book_value_per_share:14.1333,dividend_payout_ratio_pct:23,total_debt_cr:26006,cash_from_operations_cr:-1253},
  {id:1160,company_id:"ULTRACEMCO",year:"Mar 2024",net_profit_margin_pct:9.88,operating_profit_margin_pct:18,return_on_equity_pct:11.63,debt_to_equity:0.1893,interest_coverage:13.9835,asset_turnover:0.7035,free_cash_flow_cr:2109,capex_cr:8789,earnings_per_share:243,book_value_per_share:20.8401,dividend_payout_ratio_pct:29,total_debt_cr:11403,cash_from_operations_cr:10898},
  {id:1172,company_id:"UNIONBANK",year:"Mar 2024",net_profit_margin_pct:13.75,operating_profit_margin_pct:5,return_on_equity_pct:14.14,debt_to_equity:12.8237,interest_coverage:0.3536,asset_turnover:0.0716,free_cash_flow_cr:18536,capex_cr:1394,earnings_per_share:18,book_value_per_share:1.2785,dividend_payout_ratio_pct:20,total_debt_cr:1251568,cash_from_operations_cr:19930},
  {id:1184,company_id:"INDIGO",year:"Mar 2024",net_profit_margin_pct:11.85,operating_profit_margin_pct:16331,return_on_equity_pct:892.57,debt_to_equity:0.0186,interest_coverage:22.6126,asset_turnover:56.3863,free_cash_flow_cr:9424,capex_cr:11759,earnings_per_share:212,book_value_per_share:1.9062,dividend_payout_ratio_pct:0,total_debt_cr:17,cash_from_operations_cr:21183}
];

// Helper: 8 Capital Allocation Pattern Taxonomy
export function getCapitalAllocationPattern(cfo, cfi, cff) {
  const cfoPos = cfo > 0;
  const cfiNeg = cfi < 0;
  const cffNeg = cff < 0;

  if (cfoPos && cfiNeg && cffNeg) return { code: "REINVEST_RETURN", label: "Organic Compounder & Deleveraging", color: "#30D158" };
  if (cfoPos && cfiNeg && !cffNeg) return { code: "GROWTH_LEVERAGED", label: "Aggressive Expansion (Debt/Equity Funded)", color: "#0A84FF" };
  if (cfoPos && !cfiNeg && cffNeg) return { code: "DIVEST_RETURN", label: "Divestiture & Capital Return", color: "#BF5AF2" };
  if (!cfoPos && cfiNeg && !cffNeg) return { code: "EARLY_STAGE_BURNING", label: "Early Stage / Intensive CapEx", color: "#FF9F0A" };
  if (!cfoPos && !cffNeg) return { code: "OPERATIONAL_DISTRESS", label: "Distress / Survival Capital", color: "#FF453A" };
  return { code: "BALANCED_CAPITAL", label: "Prudent Operational Reinvestment", color: "#8E8E93" };
}

// Preset Screeners conforming to Section 25
export const PRESET_SCREENERS = [
  {
    id: "quality_compounder",
    name: "Quality Compounder",
    desc: "ROE > 15%, D/E < 1.0, Positive Free Cash Flow, Sustained Revenue Growth",
    filter: (r, v) => (r.return_on_equity_pct > 15) && (r.debt_to_equity < 1.0) && (r.free_cash_flow_cr > 0)
  },
  {
    id: "value_pick",
    name: "Value Pick",
    desc: "P/E < 20, P/B < 3.0, D/E < 2.0, Dividend Yield > 1%",
    filter: (r, v) => (v.pe_ratio < 20) && (v.pb_ratio < 3.0) && (r.debt_to_equity < 2.0) && (v.dividend_yield_pct > 1.0)
  },
  {
    id: "growth_accelerator",
    name: "Growth Accelerator",
    desc: "PAT Growth > 20%, OPM > 15%, D/E < 2.0",
    filter: (r, v) => (r.net_profit_margin_pct > 12) && (r.operating_profit_margin_pct > 15) && (r.debt_to_equity < 2.0)
  },
  {
    id: "dividend_champion",
    name: "Dividend Champion",
    desc: "Dividend Yield > 2%, Payout Ratio < 80%, Positive FCF",
    filter: (r, v) => (v.dividend_yield_pct > 2.0) && (r.dividend_payout_ratio_pct < 80) && (r.free_cash_flow_cr > 0)
  },
  {
    id: "debt_free_bluechips",
    name: "Debt-Free Blue Chip",
    desc: "Zero or Negligible Borrowings (D/E < 0.05), ROE > 12%",
    filter: (r, v) => (r.debt_to_equity < 0.05) && (r.return_on_equity_pct > 12)
  },
  {
    id: "turnaround_watch",
    name: "Turnaround Watch",
    desc: "Positive Cash from Operations, Recovering Net Margins",
    filter: (r, v) => (r.cash_from_operations_cr > 0) && (r.net_profit_margin_pct > 5)
  }
];

// Composite Financial Health Score (0–100) per Section 25.1 & Specification
export function computeHealthScore(ratios = {}, valuation = {}) {
  const roe = ratios.return_on_equity_pct ?? 15;
  const roce = ratios.roce ?? (roe * 1.15);
  const npm = ratios.net_profit_margin_pct ?? 12;
  const de = ratios.debt_to_equity ?? 0.5;
  const icr = ratios.interest_coverage ?? 15;
  const fcf = ratios.free_cash_flow_cr ?? 500;
  const cfo = ratios.cash_from_operations_cr ?? 1000;

  // 1. Profitability (35% weight: ROE 15%, ROCE 10%, NPM 10%)
  const roeScore = Math.min(15, Math.max(0, (roe / 25) * 15));
  const roceScore = Math.min(10, Math.max(0, (roce / 30) * 10));
  const npmScore = Math.min(10, Math.max(0, (npm / 20) * 10));
  const profScore = roeScore + roceScore + npmScore;

  // 2. Cash Quality (30% weight: FCF quality, CFO generation)
  const fcfPosScore = fcf > 0 ? 10 : 0;
  const cfoScore = cfo > 0 ? 10 : 0;
  const fcfQuality = Math.min(10, Math.max(0, fcf > 0 ? (fcf / 2000) * 10 : 0));
  const cashScore = fcfPosScore + cfoScore + fcfQuality;

  // 3. Growth (20% weight)
  const growthScore = Math.min(20, Math.max(5, (roe > 20 ? 18 : (roe > 12 ? 14 : 8))));

  // 4. Leverage (15% weight: D/E 10%, ICR 5%)
  let deScore = 10;
  if (de <= 0.05) deScore = 10;
  else if (de <= 0.5) deScore = 8.5;
  else if (de <= 1.0) deScore = 7.0;
  else if (de <= 2.0) deScore = 5.0;
  else deScore = 1.0;

  let icrScore = 5;
  if (icr >= 10 || icr === 999) icrScore = 5;
  else if (icr >= 5) icrScore = 4;
  else if (icr >= 3) icrScore = 2.5;
  else icrScore = 0.5;
  const levScore = deScore + icrScore;

  const total = Math.round(Math.min(100, Math.max(15, profScore + cashScore + growthScore + levScore)));

  // Bands per specification:
  // 80–100: Excellent (Signal Green)
  // 65–79: Good (Apple Blue)
  // 50–64: Average (Apple Amber)
  // 35–49: Weak (Muted Coral)
  // 0–34: Poor (Coral Red)
  let band = "Average";
  let color = "#FF9F0A";
  if (total >= 80) {
    band = "Excellent";
    color = "#30D158";
  } else if (total >= 65) {
    band = "Good";
    color = "#0A84FF";
  } else if (total >= 50) {
    band = "Average";
    color = "#FF9F0A";
  } else if (total >= 35) {
    band = "Weak";
    color = "#FF6961";
  } else {
    band = "Poor";
    color = "#FF453A";
  }

  return {
    score: total,
    band,
    color,
    breakdown: {
      profitability: Math.round(profScore),
      cashQuality: Math.round(cashScore),
      growth: Math.round(growthScore),
      leverage: Math.round(levScore)
    }
  };
}
