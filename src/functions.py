import supervisely as sly
import globals as g
from supervisely.imaging.color import rgb2hex
from supervisely.app.v1.widgets.grid_gallery import Gallery


def get_ann_by_id(id, current_page):
    unique_id = f"{current_page}_{id}"
    if g.cache.get(unique_id) is None:
        ann_info = g.api.annotation.download(id)
        ann_json = ann_info.annotation
        g.cache.add(unique_id, ann_json, expire=g.cache_item_expire_time)
    else:
        ann_json = g.cache.get(unique_id)
    ann = sly.Annotation.from_json(ann_json, g.meta)
    return ann


def get_info_dict(ann):
    preview_data = {"objects": len(ann.labels)}
    labelers_cnt = []
    for label in ann.labels:
        if label.geometry.labeler_login not in labelers_cnt:
            labelers_cnt.append(label.geometry.labeler_login)
    preview_data["labelers"] = len(labelers_cnt)

    classes = ann.stat_class_count(g.meta_classes_names)
    preview_data["classes"] = []
    for class_name, class_cnt in classes.items():
        if class_cnt > 0 and class_name != "total":
            obj_class = g.meta.get_obj_class(class_name)
            preview_data["classes"].append({"name": obj_class.name, "color": rgb2hex(obj_class.color)})
    return preview_data


def update_gallery_by_page(current_page, state):
    cols = state['cols']
    images_per_page = state['rows']
    max_pages_count = len(g.image_ids) // images_per_page
    if len(g.image_ids) % images_per_page != 0:
        max_pages_count += 1

    g.full_gallery = Gallery(g.task_id, g.api, 'data.perClass', g.meta, cols, preview_info=g.preview_info)

    curr_images_names = g.images_names[images_per_page * (current_page - 1):images_per_page * current_page]
    curr_images_urls = g.images_urls[images_per_page * (current_page - 1):images_per_page * current_page]

    g.curr_images_ids = g.image_ids[images_per_page * (current_page - 1):images_per_page * current_page]
    g.curr_anns = [get_ann_by_id(image_id, current_page) for image_id in g.curr_images_ids]

    curr_title_urls = g.images_labeling_urls[images_per_page * (current_page - 1):images_per_page * current_page]

    for idx, (image_name, ann, image_url, title_url) in enumerate(
            zip(curr_images_names, g.curr_anns, curr_images_urls, curr_title_urls)):
        if idx == images_per_page:
            break

        custom_info = get_info_dict(ann)

        g.full_gallery.add_item(title=image_name, ann=ann, image_url=image_url, custom_info=custom_info,
                                title_url=title_url)

    g.full_gallery.update()

    if g.DATASET_ID is not None:
        ds_images = len(g.image_ids)
    else:
        ds_images = None

    fields = [
        {"field": "state.galleryPage", "payload": current_page},
        {"field": "state.galleryMaxPage", "payload": max_pages_count},
        {"field": "state.input", "payload": current_page},
        {"field": "state.maxImages", "payload": len(g.image_ids)},
        {"field": "state.totalImages", "payload": g.total_images_in_project},
        {"field": "state.dsImages", "payload": ds_images},
        {"field": "state.rows", "payload": images_per_page},
        {"field": "state.cols", "payload": cols},
        {"field": "state.preview_info", "payload": g.preview_info},
        {"field": "state.alreadyUpload", "payload": True},
        {"field": "state.loading", "payload": False}
    ]
    g.api.app.set_fields(g.task_id, fields)
    print(state)
