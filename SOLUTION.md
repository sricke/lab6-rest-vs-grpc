
|  Method 	| Local  	| Same-Zone  	|  Different Region 	| 
|---	|---	|---	|---	|---	|
|   REST add	|  3.3 	|   4.4	| 325 	| 
|   gRPC add	|   1	|   1.1	|  152  	|
|   REST rawimg	|   6.35	|   11.6	|   1283	|
|   gRPC rawimg	|  10.5     | 12.6  	| 173 	|
|   REST dotproduct	|  4.4 	|   5.1	| 326 	|
|   gRPC dotproduct	|   1.1	|   1.3	|  157  	|
|   REST jsonimg	|   37.9	|  42.6 	|   1462	|
|   gRPC jsonimg	|   34    |   35.6	|   213	|
|   PING        |   0.05    |   0.3   |    162   |

gRPC uses a single connection and binary payloads, unlike REST.

The results show that gRPC gives more efficient communication with lower latency. For add and dotProduct, the gap between REST and gRPC is small; it becomes much larger for image operations, especially across regions, where payloads are bigger and travel farther. Even after subtracting the per-request ping latency (e.g. 162 ms in the different-region case), the difference remains large for images—binary encoding and raw bytes give gRPC a clear advantage for large payloads. RawImage is especially efficient because the image is sent as bytes directly, with no extra encoding. For lightweight operations like add and dotProduct, once ping is accounted for, the difference between REST and gRPC is less notable.