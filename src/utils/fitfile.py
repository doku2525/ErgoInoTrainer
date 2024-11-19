import fitdecode


def list_of_frame_names(fit_datei: str) -> set[str]:
    with fitdecode.FitReader(fit_datei) as fit:
        return set([frame.name for frame in fit if frame.frame_type == fitdecode.FIT_FRAME_DATA])


def get_alle_frames_mit_namen(fit_datei: str, frame_name: str) -> list[fitdecode.FIT_FRAME_DATA]:
    with fitdecode.FitReader(fit_datei) as fit:
        return [frame for frame in fit if frame.frame_type == fitdecode.FIT_FRAME_DATA and frame.name == frame_name]


def get_alle_fieldnames_of_frames(fit_datei: str, frame_name: str) -> set[str]:
    return set([field.name for frame in get_alle_frames_mit_namen(fit_datei, frame_name) for field in frame.fields])
