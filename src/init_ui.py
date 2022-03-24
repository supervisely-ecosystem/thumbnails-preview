import globals as g


def init(data, state):
    data["perClass"] = None
    data["projectId"] = g.project_info.id
    data["projectName"] = g.project_info.name
    data["projectPreviewUrl"] = g.api.image.preview_url(g.project_info.reference_image_url, 100, 100)
    data["projectTotalImages"] = g.total_images_in_project
    if g.DATASET_ID is not None:
        data["datasetPreviewUrl"] = g.api.image.preview_url(g.dataset_preview_image.full_storage_url, 100, 100)
        data["datasetId"] = g.dataset_info.id
        data["datasetName"] = g.dataset_info.name
        data["datasetTotalImages"] = g.total_images_in_dataset

    state['alreadyUpload'] = False
    state['galleryPage'] = g.first_page
    state['rows'] = g.images_on_page
    state['cols'] = g.columns_on_page

    state["galleryMaxPage"] = None
    state["input"] = None
    state["maxImages"] = None
    state["totalImages"] = g.total_images_in_project
    state["dsImages"] = None
    state["preview_info"] = g.preview_info
    state["loading"] = True