import grpc
from concurrent import futures
from PIL import Image
import io
import server_pb2
import server_pb2_grpc
import base64
class Server(server_pb2_grpc.ServerServicer):
    
    def Add(self, request, context):
        return server_pb2.addReply(sum=request.a + request.b)
    
    def RawImage(self, request, context):
        img = Image.open(io.BytesIO(request.img)) #byteos io for reading bytes
        return server_pb2.imageReply(width=img.width, height=img.height)
    
    def DotProduct(self, request, context):
        return server_pb2.dotProductReply(dotproduct=sum(request.a[i] * request.b[i] for i in range(len(request.a))))
    
    def JsonImage(self, request, context):
        image_decoded = base64.b64decode(request.img)
        img = Image.open(io.BytesIO(image_decoded))
        return server_pb2.imageReply(width=img.width, height=img.height)
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server_pb2_grpc.add_ServerServicer_to_server(Server(), server)
    server.add_insecure_port("[::]:5001")
    server.start()
    server.wait_for_termination() 
    
if __name__ == "__main__":
    serve()