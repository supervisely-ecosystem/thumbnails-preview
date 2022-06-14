import os
import supervisely as sly
from diskcache import Cache
from supervisely.io.fs import mkdir
from supervisely.app.v1.app_service import AppService

my_app: AppService = AppService()

api: sly.Api = my_app.public_api
task_id = my_app.task_id

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
PROJECT_ID = int(os.environ['modal.state.slyProjectId'])
DATASET_ID = os.environ.get('modal.state.slyDatasetId', None)

stats = api.project.get_stats(PROJECT_ID)

if DATASET_ID is not None:
    DATASET_ID = int(DATASET_ID)

project = None
datasets = None

total_images_in_dataset = None
if DATASET_ID is not None:
    dataset_info = api.dataset.get_info_by_id(DATASET_ID)
    datasets = [dataset_info]
    dataset_preview_image = api.image.get_list(dataset_info.id, sort="name")[0]

    for item in stats["datasets"]["items"]:
        if item["id"] == DATASET_ID:
            total_images_in_dataset = item["imagesCount"]

project_info = api.project.get_info_by_id(PROJECT_ID)
total_images_in_project = stats["datasets"]["total"]["imagesCount"]

if datasets is None:
    datasets = api.dataset.get_list(PROJECT_ID)

meta_json = api.project.get_meta(project_info.id)
meta = sly.ProjectMeta.from_json(meta_json)

all_images = []
images_labeling_urls = []
for dataset in datasets:
    images = api.image.get_list(dataset.id, sort="name")
    all_images.extend(images)
    for image in images:
        image_labeling_url = f"/app/images/{TEAM_ID}/{WORKSPACE_ID}/{PROJECT_ID}/{dataset.id}#image-{image.id}"
        images_labeling_urls.append(image_labeling_url)

image_ids = [image_info.id for image_info in all_images]
images_urls = [image_info.path_original for image_info in all_images]
images_names = [image_info.name for image_info in all_images]

work_dir = os.path.join(my_app.cache_dir, "work_dir")
mkdir(work_dir, True)
cache_dir = os.path.join(work_dir, "diskcache")
mkdir(cache_dir)
cache = Cache(directory=cache_dir)
cache_item_expire_time = 600  # seconds

images_on_page = 30
columns_on_page = 5
first_page = 1
preview_input = None
preview_rows = None
preview_info = True
full_gallery = None
curr_images_ids = None
curr_anns = None