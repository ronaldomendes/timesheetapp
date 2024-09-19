# Time Sheet App

### Some steps to create a custom multi-platform docker image:
- Locally login into your docker account: ``docker login``
- Create a custom builder: ``docker buildx create --name multibuilder --driver docker-container --bootstrap --use``
- To create a new image and send into your docker account: ``docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t docker_user/timesheetapp:latest --push .``
