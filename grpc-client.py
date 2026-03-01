import grpc
import server_pb2
import server_pb2_grpc
import random
import base64
import sys
import time


def doAdd(stub):
    response = stub.Add(server_pb2.addMsg(a=1, b=2))
    print(response.sum)

def doRawImage(stub):
    image = open('Flatirons_Winter_Sunrise_edit_2.jpg', 'rb').read()# only as bytes
    response = stub.RawImage(server_pb2.rawImageMsg(img=image))
    print(response.width, response.height)

def doDotProduct(stub):
    response = stub.DotProduct(server_pb2.dotProductMsg(a=[random.random() for _ in range(100)], b=[random.random() for _ in range(100)]))
    print(response.dotproduct)
    
def doJsonImage(stub):
    image = open('Flatirons_Winter_Sunrise_edit_2.jpg', 'rb').read()
    response = stub.JsonImage(server_pb2.jsonImageMsg(img=base64.b64encode(image).decode('utf-8'))) # as string
    print(response.width, response.height)
    
if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} <server ip> <cmd> <reps>")
    print(f"where <cmd> is one of add, rawImage, sum or jsonImage")
    print(f"and <reps> is the integer number of repititions for measurement")

host = sys.argv[1]
cmd = sys.argv[2]
reps = int(sys.argv[3])


channel = grpc.insecure_channel(f'{host}:5001')
stub = server_pb2_grpc.ServerStub(channel)
if cmd == 'rawImage':
    start = time.perf_counter()
    for x in range(reps):
        doRawImage(stub)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
elif cmd == 'add':
    start = time.perf_counter()
    for x in range(reps):
        doAdd(stub)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
elif cmd == 'jsonImage':
    start = time.perf_counter()
    for x in range(reps):
        doJsonImage(stub)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
elif cmd == 'dotProduct':
    start = time.perf_counter()
    for x in range(reps):
        doDotProduct(stub)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
else:
    print("Unknown option", cmd)