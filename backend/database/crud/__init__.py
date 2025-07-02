from .delete import (
    delete_oee_setup,
    delete_digest_data,
    delete_planned_downtime_setup,
    delete_unplanned_downtime_setup,
    delete_paradas,
    delete_planned_downtime,
    delete_unplanned_downtime,
    delete_auto_oee
)

from .create import (
    create_oee_setup,
    create_digest_data,
    create_planned_downtime_setup,
    create_unplanned_downtime_setup,
    create_parada,
    create_planned_downtime,
    create_unplanned_downtime,
    create_auto_oee
)

from .read import (
    get_all_oee_setups,
    get_all_digest_data,
    get_all_planned_downtime_setups,
    get_all_unplanned_downtime_setups,
    get_all_paradas,
    get_all_planned_downtime,
    get_all_unplanned_downtime,
    get_all_auto_oee,

    get_oee_setup_by_id,
    get_digest_data_by_id,
    get_planned_downtime_setup_by_id,
    get_unplanned_downtime_setup_by_id,
    get_parada_by_id,
    get_planned_downtime_by_id,
    get_unplanned_downtime_by_id,
    get_auto_oee_by_id,

    get_digest_data_by_camera_name_id,
    get_oee_setup_by_camera_name_id,
    get_planned_downtime_setup_by_camera_name_id,
    get_last_digest_data_by_camera,
    get_last_parada_by_camera,
    get_last_auto_oee_by_camera,
    
)

from .special_read import (
    get_auto_oee_by_period_and_camera,
    get_digest_data_filtered_by_stop_and_cameraId,
    get_digest_data_filtered_by_period_and_cameraId,
    get_total_planned_downtime_seconds,
    get_total_unplanned_downtime_seconds,
    get_total_nonjustified_downtime_seconds,
    get_total_ok_nok_from_digest,
    get_total_ok_nok_discretized_by_period,
    get_total_ok_nok_grouped_by_rows,
    get_planned_downtime_filtered_by_init_end_cameraId,
    get_paradas_com_tipo,
    get_resumo_paradas_by_period
)

from .update import (
    update_oee_setup,
    update_digest_data,
    update_planned_downtime_setup,
    update_unplanned_downtime_setup,
    update_paradas,
    update_planned_downtime,
    update_unplanned_downtime,
    update_auto_oee
)