import supervisely as sly
import globals as g
import init_ui
import functions as f


@g.my_app.callback("init_gallery")
@sly.timeit
def init_gallery(api: sly.Api, task_id, context, state, app_logger):
    # api.task.set_field(task_id, "state.alreadyUpload", True)
    g.preview_input = state['galleryPage']
    current_page = g.first_page
    f.update_gallery_by_page(current_page, state)


@g.my_app.callback("update_page")
@sly.timeit
def update_page(api: sly.Api, task_id, context, state, app_logger):
    fields = [
        {"field": "state.alreadyUpload", "payload": False},
        {"field": "state.loading", "payload": True}
    ]
    api.task.set_fields(task_id, fields)
    go_to_page = state.get('input')
    current_page = int(go_to_page)
    if g.preview_input > current_page and g.preview_rows != state['rows']:
        current_page = g.first_page
    g.preview_rows = state['rows']
    f.update_gallery_by_page(current_page, state)


def main():
    sly.logger.info("Script arguments", extra={
        "context.teamId": g.TEAM_ID,
        "context.workspaceId": g.WORKSPACE_ID,
        "data.projectId": g.PROJECT_ID
    })

    data = {}
    state = {}

    init_ui.init(data, state)

    g.my_app.run(state=state, data=data, initial_events=[{"state": state, "command": "init_gallery"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main)
