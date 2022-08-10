from rest_framework import serializers

from smartInventory_common.utils.job import JobStatus


class JobSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    start_date = serializers.DateTimeField(read_only=True)
    end_date = serializers.DateTimeField(read_only=True, allow_null=True)
    job_type = serializers.CharField(max_length=50, read_only=True)
    job_status = serializers.ChoiceField(choices=JobStatus.choices, read_only=True)
    pod_id = serializers.CharField(max_length=255, read_only=True)
    logs = serializers.CharField(max_length=512, read_only=True)
    last_update = serializers.DateTimeField(read_only=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
