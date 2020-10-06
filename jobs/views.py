from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from .models import job
from django.http import JsonResponse
from .permissions import IsOwnerOrReadOnly, IsAuthenticated
from .serializers import jobserializer
from .serializers import TaskResultserializer
from .pagination import CustomPagination
from jobs import joblist
from django_celery_results.models import TaskResult
from crack import celery_app


class get_delete_update_job(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskResultserializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly,)

    def get_queryset(self, pk):
        try:
            jobins = TaskResult.objects.get(task_id=pk)

        except TaskResult.DoesNotExist:
            content = {
                'status': 'Not Found'
            }
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        return jobins

    # Get a job
    def get(self, request, pk):

        try:
            jobins = TaskResult.objects.get(task_id=pk)

        except TaskResult.DoesNotExist:
            content = {
                'status': 'Not Found'
            }
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskResultserializer(jobins)

        # if serializer.is_valid():
        #     print("serializer.data...")
        #     print(serializer.data)
        #
        # print(serializer.errors)

        obj = job.objects.get(resultid=pk)
        print("user name.....")
        print(obj.creator.username)

        serializer.username = obj.creator.username

        response_data = {'status': 'True', 'msg': '任务获取成功!', 'data': {
            "meta": {},
            "result": [
                {
                    "id": jobins.task_id,
                    "status": jobins.status,
                    "user_name": obj.creator.username,
                    "result": jobins.result,
                    "hash": obj.hash,
                }
            ]
        }}

        return Response(response_data, status=status.HTTP_200_OK)

    # Update a job
    def put(self, request, pk):

        obj = job.objects.get(resultid=pk)

        if request.user == obj.creator.username:  # If creator is who makes request
            serializer = jobserializer(job, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            content = {
                'status': 'UNAUTHORIZED'
            }
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)

    # Delete a job
    def delete(self, request, pk):

        try:
            obj = job.objects.get(resultid=pk)
        except job.DoesNotExist:
            response_data = {'status': 'False', 'msg': '任务不存在!', 'data': {
                "meta": {},
                "result": [

                ]
            }}
            return Response(response_data, status=status.HTTP_200_OK)

        if request.user == obj.creator:  # If creator is who makes request
            celery_app.control.revoke(pk)
            obj.delete()
            jobresult = TaskResult.objects.get(task_id=pk)
            jobresult.delete()
            response_data = {'status': 'True', 'msg': '任务删除成功!', 'data': {
                "meta": {},
                "result": [

                ]
            }}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            content = {
                'status': 'UNAUTHORIZED'
            }
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)

    # cancel a job
    def post(self, request, pk):

        try:
            obj = job.objects.get(resultid=pk)
        except job.DoesNotExist:
            response_data = {'status': 'False', 'msg': '任务不存在!', 'data': {
                "meta": {},
                "result": [

                ]
            }}
            return Response(response_data, status=status.HTTP_200_OK)

        if request.user == obj.creator:  # If creator is who makes request
            celery_app.control.revoke(pk)

            response_data = {'status': 'True', 'msg': '任务取消成功!', 'data': {
                "meta": {},
                "result": [
                ]
            }}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            content = {
                'status': 'UNAUTHORIZED'
            }
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)


class get_post_jobs(ListCreateAPIView):
    serializer_class = TaskResultserializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_queryset(self):
        jobs = TaskResult.objects.all()
        return jobs

    # Get all jobs
    def get(self, request):
        jobins = self.get_queryset()
        result = []

        for record in jobins:
            obj = job.objects.get(resultid=record.task_id)
            result.append({
                "id": record.task_id,
                "status": record.status,
                "user_name": obj.creator.username,
                "result": record.result,
                "hash": obj.hash,
            })

        response_data = {'status': 'True', 'msg': '任务获取成功!', 'data': {
            "meta": {},
            "result": result
        }}

        return Response(response_data, status=status.HTTP_200_OK)

    # Create a new job
    def post(self, request):
        serializer = jobserializer(data=request.data)

        if serializer.is_valid():
            hashstr = request.data['hash']
            ret = joblist.pojie.delay(hashstr)

            serializer.save(creator=request.user, resultid=ret.task_id)
            response_data = {'status': 'True', 'msg': '任务提交成功!', 'data': {
                "meta": {},
                "result": [
                    {
                        "id": ret.task_id,
                        "status": 0,
                        "result": ret.result
                    }
                ]
            }}
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
