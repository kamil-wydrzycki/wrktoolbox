import pytest
from wrktoolbox.wrkoutput import (BenchmarkOutput,
                                  LatencyResult,
                                  LatencyDistributionResult,
                                  ValueResult,
                                  SocketErrorsResult,
                                  HdrHistogramLatencyDistributionResult,
                                  reqs_count_pattern)


@pytest.mark.parametrize('value,expected_average_latency', [
    ['Latency   196.94ms  183.71ms 944.41ms   89.18%', ValueResult(196.94, 'ms')],
])
def test_parse_latency(value, expected_average_latency):
    result = LatencyResult.parse(value)
    assert expected_average_latency == result.avg


@pytest.mark.parametrize('value,expected_50_percentile,expected_50_percentile_unit,'
                         'expected_75_percentile,expected_75_percentile_unit,'
                         'expected_90_percentile,expected_90_percentile_unit,'
                         'expected_99_percentile,expected_99_percentile_unit', [
    [
        """
          Latency Distribution
             50%  911.84ms
             75%    1.44s
             90%    1.50s
             99%    1.54s 
        """, 911.84, 'ms', 1.44, 's', 1.5, 's', 1.54, 's'
    ],
    [
        """
          Latency Distribution
             50%  111.84ms
             75%    601.44ms
             90%    900.50ms
             99%    1.0s 
        """, 111.84, 'ms', 601.44, 'ms', 900.50, 'ms', 1.0, 's'
    ]
])
def test_parse_latency_distribution(value,
                                    expected_50_percentile,
                                    expected_50_percentile_unit,
                                    expected_75_percentile,
                                    expected_75_percentile_unit,
                                    expected_90_percentile,
                                    expected_90_percentile_unit,
                                    expected_99_percentile,
                                    expected_99_percentile_unit):
    result = LatencyDistributionResult.parse(value)
    assert expected_50_percentile == result.percentiles[50].value
    assert expected_50_percentile_unit == result.percentiles[50].unit
    assert expected_75_percentile == result.percentiles[75].value
    assert expected_75_percentile_unit == result.percentiles[75].unit
    assert expected_90_percentile == result.percentiles[90].value
    assert expected_90_percentile_unit == result.percentiles[90].unit
    assert expected_99_percentile == result.percentiles[99].value
    assert expected_99_percentile_unit == result.percentiles[99].unit


@pytest.mark.parametrize('value,connect_errors,read_errors,write_errors,timeout_errors', [
    [
        'Socket errors: connect 0, read 0, write 0, timeout 1463',
        0, 0, 0, 1463
    ],
    [
        'Socket errors: connect 10, read 2, write 30, timeout 15',
        10, 2, 30, 15
    ]
])
def test_parse_socket_errors(value, connect_errors, read_errors, write_errors, timeout_errors):
    result = SocketErrorsResult.parse(value)
    assert connect_errors == result.connect_errors
    assert read_errors == result.read_errors
    assert write_errors == result.write_errors
    assert timeout_errors == result.timeout_errors


@pytest.mark.parametrize('raw_output,'
                         'expected_requests_per_second,'
                         'expected_transfer_per_second,'
                         'expected_average_latency,'
                         'expected_has_errors,'
                         'expected_latency_distribution,'
                         'expected_socket_errors,'
                         'expected_not_successful_responses', [
    [
        """
        Running 30s test @ https://foo.org/
          12 threads and 400 connections
          Thread Stats   Avg      Stdev     Max   +/- Stdev
            Latency     1.49s   329.38ms   2.00s    73.97%
            Req/Sec    35.90     39.35   170.00     83.51%
          4294 requests in 30.09s, 2.06MB read
          Socket errors: connect 0, read 0, write 0, timeout 1463
        Requests/sec:    142.72
        Transfer/sec:     70.09KB
        """, 142.72, ValueResult(70.09, 'KB'), ValueResult(1.49, 's'), True, None, SocketErrorsResult(0, 0, 0, 1463), 0
    ],
    [
        """
        Running 30s test @ https://foo.org/
          10 threads and 10 connections
          Thread Stats   Avg      Stdev     Max   +/- Stdev
            Latency   376.96ms  268.10ms   1.25s    72.09%
            Req/Sec     4.72      4.12    10.00     58.49%
          Latency Distribution
             50%  454.07ms
             75%  555.73ms
             90%  625.97ms
             99%    1.24s
          829 requests in 30.06s, 294.68KB read
          Non-2xx or 3xx responses: 829
        Requests/sec:     27.58
        Transfer/sec:      9.80KB
        """, 27.58, ValueResult(9.80, 'KB'), ValueResult(376.96, 'ms'), True, {50: ValueResult(454.07, 'ms'),
                                                                               75: ValueResult(555.73, 'ms'),
                                                                               90: ValueResult(625.97, 'ms'),
                                                                               99: ValueResult(1.24, 's')},
        None, 829
    ],
    [
        """
        Running 30s test @ https://foo.org/hello-world
          10 threads and 10 connections
          Thread calibration: mean lat.: 180.088ms, rate sampling interval: 506ms
          Thread calibration: mean lat.: 162.800ms, rate sampling interval: 429ms
          Thread calibration: mean lat.: 174.576ms, rate sampling interval: 508ms
          Thread calibration: mean lat.: 170.760ms, rate sampling interval: 428ms
          Thread calibration: mean lat.: 161.920ms, rate sampling interval: 462ms
          Thread calibration: mean lat.: 171.016ms, rate sampling interval: 481ms
          Thread calibration: mean lat.: 180.112ms, rate sampling interval: 517ms
          Thread calibration: mean lat.: 178.272ms, rate sampling interval: 479ms
          Thread calibration: mean lat.: 178.160ms, rate sampling interval: 498ms
          Thread calibration: mean lat.: 181.696ms, rate sampling interval: 499ms
          Thread Stats   Avg      Stdev     Max   +/- Stdev
            Latency   161.91ms  150.49ms 876.03ms   95.00%
            Req/Sec     0.33      0.70     2.00    100.00%
          Latency Distribution (HdrHistogram - Recorded Latency)
         50.000%  129.15ms
         75.000%  142.46ms
         90.000%  148.09ms
         99.000%  873.98ms
         99.900%  876.54ms
         99.990%  876.54ms
         99.999%  876.54ms
        100.000%  876.54ms
        
          Detailed Percentile spectrum:
               Value   Percentile   TotalCount 1/(1-Percentile)
        
              56.127     0.000000            1         1.00
             107.519     0.100000            8         1.11
             113.855     0.200000           16         1.25
             122.367     0.300000           24         1.43
             126.143     0.400000           32         1.67
             129.151     0.500000           40         2.00
             129.919     0.550000           44         2.22
             136.959     0.600000           48         2.50
             141.055     0.650000           52         2.86
             141.439     0.700000           56         3.33
             142.463     0.750000           60         4.00
             142.975     0.775000           62         4.44
             144.127     0.800000           64         5.00
             145.535     0.825000           66         5.71
             146.431     0.850000           68         6.67
             146.943     0.875000           70         8.00
             147.967     0.887500           71         8.89
             148.095     0.900000           72        10.00
             149.887     0.912500           73        11.43
             150.015     0.925000           74        13.33
             150.655     0.937500           75        16.00
             153.983     0.943750           76        17.78
             153.983     0.950000           76        20.00
             590.335     0.956250           77        22.86
             590.335     0.962500           77        26.67
             872.447     0.968750           78        32.00
             872.447     0.971875           78        35.56
             872.447     0.975000           78        40.00
             873.983     0.978125           79        45.71
             873.983     0.981250           79        53.33
             873.983     0.984375           79        64.00
             873.983     0.985938           79        71.11
             873.983     0.987500           79        80.00
             876.543     0.989062           80        91.43
             876.543     1.000000           80          inf
        #[Mean    =      161.908, StdDeviation   =      150.488]
        #[Max     =      876.032, Total count    =           80]
        #[Buckets =           27, SubBuckets     =         2048]
        ----------------------------------------------------------
          120 requests in 30.01s, 42.66KB read
          Socket errors: connect 0, read 0, write 0, timeout 20
          Non-2xx or 3xx responses: 120
        Requests/sec:      4.00
        Transfer/sec:      1.42KB
        """, 4.00, ValueResult(1.42, 'KB'), ValueResult(161.91, 'ms'), True, {50.000: ValueResult(129.15, 'ms'),
                                                                              75.000: ValueResult(142.46, 'ms'),
                                                                              90.000: ValueResult(148.09, 'ms'),
                                                                              99.000: ValueResult(873.98, 'ms'),
                                                                              99.900: ValueResult(876.54, 'ms'),
                                                                              99.990: ValueResult(876.54, 'ms'),
                                                                              99.999: ValueResult(876.54, 'ms'),
                                                                              100.000: ValueResult(876.54, 'ms')},
        SocketErrorsResult(0, 0, 0, 20), 120
    ],
    [
        """
        Running 2s test @ https://foo.org/hello-world
          10 threads and 100 connections
          Thread Stats   Avg      Stdev     Max   +/- Stdev
            Latency     1.32s   417.78ms   1.95s    54.00%
            Req/Sec       -nan      -nan   0.00      0.00%
          Latency Distribution (HdrHistogram - Recorded Latency)
         50.000%    1.37s 
         75.000%    1.69s 
         90.000%    1.75s 
         99.000%    1.93s 
         99.900%    1.95s 
         99.990%    1.95s 
         99.999%    1.95s 
        100.000%    1.95s 
        
          Detailed Percentile spectrum:
               Value   Percentile   TotalCount 1/(1-Percentile)
        
             668.159     0.000000            1         1.00
             835.071     0.100000           10         1.11
             847.359     0.200000           20         1.25
             861.695     0.300000           30         1.43
             945.663     0.400000           40         1.67
            1373.183     0.500000           50         2.00
            1618.943     0.550000           55         2.22
            1633.279     0.600000           60         2.50
            1646.591     0.650000           65         2.86
            1662.975     0.700000           70         3.33
            1690.623     0.750000           75         4.00
            1718.271     0.775000           78         4.44
            1721.343     0.800000           80         5.00
            1727.487     0.825000           83         5.71
            1733.631     0.850000           85         6.67
            1744.895     0.875000           88         8.00
            1746.943     0.887500           89         8.89
            1751.039     0.900000           90        10.00
            1793.023     0.912500           92        11.43
            1794.047     0.925000           93        13.33
            1800.191     0.937500           94        16.00
            1889.279     0.943750           95        17.78
            1889.279     0.950000           95        20.00
            1903.615     0.956250           97        22.86
            1903.615     0.962500           97        26.67
            1903.615     0.968750           97        32.00
            1926.143     0.971875           98        35.56
            1926.143     0.975000           98        40.00
            1926.143     0.978125           98        45.71
            1927.167     0.981250           99        53.33
            1927.167     0.984375           99        64.00
            1927.167     0.985938           99        71.11
            1927.167     0.987500           99        80.00
            1927.167     0.989062           99        91.43
            1946.623     0.990625          100       106.67
            1946.623     1.000000          100          inf
        #[Mean    =     1320.632, StdDeviation   =      417.780]
        #[Max     =     1945.600, Total count    =          100]
        #[Buckets =           27, SubBuckets     =         2048]
        ----------------------------------------------------------
          100 requests in 2.05s, 78.71KB read
        Requests/sec:     48.72
        Transfer/sec:     38.35KB
        """, 48.72, ValueResult(38.35, 'KB'), ValueResult(1.32, 's'), False, {50.000: ValueResult(1.37, 's'),
                                                                              75.000: ValueResult(1.69, 's'),
                                                                              90.000: ValueResult(1.75, 's'),
                                                                              99.000: ValueResult(1.93, 's'),
                                                                              99.900: ValueResult(1.95, 's'),
                                                                              99.990: ValueResult(1.95, 's'),
                                                                              99.999: ValueResult(1.95, 's'),
                                                                              100.000: ValueResult(1.95, 's')},
        None, 0
    ]
])
def test_parse_output(raw_output,
                      expected_requests_per_second,
                      expected_transfer_per_second,
                      expected_average_latency,
                      expected_has_errors,
                      expected_latency_distribution,
                      expected_socket_errors,
                      expected_not_successful_responses):
    result = BenchmarkOutput.parse(raw_output)
    assert expected_average_latency == result.latency.avg
    assert expected_requests_per_second == result.requests_per_second
    assert expected_transfer_per_second == result.transfer_per_second
    assert expected_has_errors == result.has_errors
    assert expected_latency_distribution == result.latency_distribution
    assert expected_socket_errors == result.socket_errors
    assert expected_not_successful_responses == result.not_successful_responses


@pytest.mark.parametrize('value,expected_count,expected_seconds,expected_size,expected_size_unit', [
    ['4294 requests in 30.09s, 2.06MB read', '4294', '30.09', '2.06', 'MB'],
    ['   4294 requests in 30.09s, 2.06MB read', '4294', '30.09', '2.06', 'MB'],
])
def test_parse_requests_line(value, expected_count, expected_seconds, expected_size, expected_size_unit):
    result = reqs_count_pattern.parseString(value)
    assert result.reqs_count == expected_count
    assert result.seconds_count == expected_seconds
    assert result.total_transfer_read == expected_size
    assert result.total_transfer_read_unit == expected_size_unit


@pytest.mark.parametrize('value,expected_50', [
    [
        """  
        Latency Distribution (HdrHistogram - Recorded Latency)
         50.000%    0.00us
         75.000%    0.00us
         90.000%    0.00us
         99.000%    0.00us
         99.900%    0.00us
         99.990%    0.00us
         99.999%    0.00us
        100.000%    0.00us
        """, ValueResult(0.00, 'us')
    ]
])
def test_hdr_histogram(value, expected_50):
    result = HdrHistogramLatencyDistributionResult.parse(value)

    assert result is not None
    assert result.percentiles[50.000] == expected_50

