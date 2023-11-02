import re
import json
from sipecamDeployments.helpers import parse_to_utc, add_attachments

"""
Clean kobo reports to better access the desired
data of the survey. This file contains a function
for each type of survey, wheter to be a deployment
survey, a individual survey, etc.

"""
def remove_white_spaces(text):
    parts = re.split(r"""("[^"]*"|'[^']*')""", text)
    parts[::2] = map(lambda s: "".join(s.split()), parts[::2]) # outside quotes
    return "".join(parts)

def parse_config(config, spectrum):
    warn = False
    warn_message = "Configuration needed manipulation to accomplish correct parsing. See original configuration text for reference."
    error_message = "Could not parse configuration text after correction attempts."

    wmes = None
    emes = None
    config_ = remove_white_spaces(config[1])
    config_text = config_

    try:
        conf = json.loads(config[1])
    except:
        if len(config_) < 2:
            return None, config_text, True, True
        if config_[-1] != "}":
            if config_[-2] == "}":
                config_ = config_[:-1]
            else:
                config_ = config_+"}"
        try:
            conf = json.loads(config_)
        except:
            if config_[0] != "{":
                if config_[1] == "{":
                    config_ = config_[1:]
                else:
                    config_ = "{"+config_
            try:
                conf = json.loads(config_)
            except:
                spl = config_.split('"{"')
                if len(spl) > 1:
                    config_ = "{"+spl[1]
                    return parse_config(config_, spectrum)
                else:
                    return None, config_text, warn_message, error_message
        warn = True

    if "No" in conf:
        info = conf["No"]
    else:
        info = conf["deviceInfo"]

    if warn:
        wmes = warn_message

    return info, config_text, wmes, None

def clean_kobo_deployment_report(survey):
    """
    Returns the desired data for a deployment survey.

    Parameters:
        survey (dict):      A dict containing the survey data
                            as well as its name and url.

    Returns:
        clean_data (list):  A list containing the clean survey
                            data.
    """

    entries = []
    for report in survey["reports"]:
        # obtaing kay-value pair for gps question in survey
        gps = [(key, value) for key, value in report.items() if key.startswith("_Con_cu_l_dispositivo_registra")]
        deployment_date_utc = parse_to_utc(report["Fecha_y_Hora"])
        kobo_id = report["_id"]
        kobo_formhub_uiid = report["formhub/uuid"]

        if "c_mara_trampa" in report["Dispositivo"]:
            # obtaing kay-value pair for device serial question in survey
            serial = [(key, value) for key, value in report.items() if key.startswith("Registre_el_n_mero_s_e_la_C_mara_Trampa")]

            if "Registre_la_ubicaci_n_de_la_C_mara" in report.keys():
                """
                    If string matches, then cellphone was used for
                    location record
                """
                latlng = [(key, value) for key, value in report.items() if key.startswith("Registre_la_ubicaci_n_de_la_C_mara")]
                lat = latlng[0][1].split(" ")[0]
                lng = latlng[0][1].split(" ")[1]
            else:
                """
                    If not, then gps was used for location record,
                    and so, the lat/long was recorded in two fields
                """
                lat = [(key, value) for key, value in report.items() if key.startswith("Latitud_en_grados_de_e_coloc_la")][0][1]
                lng = [(key, value) for key, value in report.items() if key.startswith("Longitud_en_grados_d_e_coloc_la")][0][1]


            # deployment data dict
            data = {
                "kobo_url": survey["kobo_url"],
                "kobo_id": kobo_id,
                "kobo_formhub_uiid": kobo_formhub_uiid,
                "date_deployment": deployment_date_utc,
                "device_type": "camera",
                "device_code": serial[0][1],
                "device_serial": serial[0][1],
                "device_specs": {},
                "latitude": lat,
                "longitude": lng,
                "metadata": add_attachments(report,survey["content"])
            }

            entries.append(data)

        elif "grabadora_audi" in report["Dispositivo"]:
            ultrasonic_serial = [(key, value) for key, value in report.items()
                    if key.startswith("Registre_el_n_mero_s_er_par_de_grabadoras")
                        or key.startswith("Registre_el_n_mero_s_do_par_de_grabadoras") and "001" in key][0]
            audible_serial = [(key, value) for key, value in report.items()
                    if key.startswith("Registre_el_n_mero_s_er_par_de_grabadoras")
                        or key.startswith("Registre_el_n_mero_s_do_par_de_grabadoras") and "001" not in key][0]
            ultrasonic_config = [(key, value) for key, value in report.items()
                    if key.startswith("Copiar_y_pegar_texto_Sipecam") and "001" in key][0]
            audible_config = [(key, value) for key, value in report.items()
                    if key.startswith("Copiar_y_pegar_texto_Sipecam") and "001" not in key][0]

            if gps[0][1] == "celular__recomendado":
                """
                    If string matches with gqp answer, then cellphone
                    was used for location record
                """
                latlng = [(key, value) for key, value in report.items()
                    if key.startswith("Registre_la_posici_n_er_par_de_grabadoras")
                        or key.startswith("Registre_la_posici_n_do_par_de_grabadoras")]

                lat = latlng[0][1].split(" ")[0]
                lng = latlng[0][1].split(" ")[1]
            else:
                """
                    If not, then gps was used for location record,
                    and so, the lat/long was recorded in two fields
                """
                lat = [(key, value) for key, value in report.items()
                            if key.startswith("Latitud_en_grados_de_audible_ultras_nica")][0][1]

                # theres a typo for this question, so in order to obtain the data
                # if has to check for the two strings, with typo and without it
                lng = [(key, value) for key, value in report.items()
                            if key.startswith("Longitud_en_grados_d_audible_ultras_nica")
                                or key.startswith("Longituden_grados_de_audible_ultras_nica")][0][1]

            udinfo, udtext, udinfo_warn, udinfo_error = parse_config(ultrasonic_config, "ultrasonic")
            if not udinfo_error:
                ultrasonic_data = {
                    "kobo_url": survey["kobo_url"],
                    "kobo_id": kobo_id,
                    "kobo_formhub_uiid": kobo_formhub_uiid,
                    "date_deployment": deployment_date_utc,
                    "device_type": "sound recorder",
                    "device_code": ultrasonic_serial[1],
                    "device_serial": udinfo["deviceId"],
                    "device_specs": {"config": udtext,
                                     "config_date": udinfo["date"],
                                     "config_spectrum": "ultrasonic",
                                     "config_warning": udinfo_warn},
                    "latitude": lat,
                    "longitude": lng,
                    "metadata": add_attachments(report,survey["content"])
                }
            else:
                ultrasonic_data = {
                    "kobo_url": survey["kobo_url"],
                    "kobo_id": kobo_id,
                    "kobo_formhub_uiid": kobo_formhub_uiid,
                    "date_deployment": deployment_date_utc,
                    "device_type": "sound recorder",
                    "device_code": ultrasonic_serial[1],
                    "device_serial": None,
                    "device_specs": {"config": udtext,
                                     "config_date": None,
                                     "config_spectrum": "ultrasonic",
                                     "config_warning": udinfo_warn},
                    "latitude": lat,
                    "longitude": lng,
                    "metadata": add_attachments(report,survey["content"])
                }
            entries.append(ultrasonic_data)

            adinfo, adtext, adinfo_warn, adinfo_error = parse_config(audible_config, "audible")
            if not adinfo_error:
                audible_data = {
                    "kobo_url": survey["kobo_url"],
                    "kobo_id": kobo_id,
                    "kobo_formhub_uiid": kobo_formhub_uiid,
                    "date_deployment": deployment_date_utc,
                    "device_type": "sound recorder",
                    "device_code": audible_serial[1],
                    "device_serial": adinfo["deviceId"],
                    "device_specs": {"config": adtext,
                                     "config_date": adinfo["date"],
                                     "config_spectrum": "audible",
                                     "config_warning": adinfo_warn},
                    "latitude": lat,
                    "longitude": lng,
                    "metadata": add_attachments(report,survey["content"])
                }
            else:
                audible_data = {
                    "kobo_url": survey["kobo_url"],
                    "kobo_id": kobo_id,
                    "kobo_formhub_uiid": kobo_formhub_uiid,
                    "date_deployment": deployment_date_utc,
                    "device_type": "sound recorder",
                    "device_code": audible_serial[1],
                    "device_serial": None,
                    "device_specs": {"config": adtext,
                                     "config_date": None,
                                     "config_spectrum": "audible",
                                     "config_warning": adinfo_warn},
                    "latitude": lat,
                    "longitude": lng,
                    "metadata": add_attachments(report,survey["content"])
                }

            entries.append(audible_data)


    return entries

def clean_kobo_individual_report(survey):
    """
    Returns the desired data for a individual survey.

    Parameters:
        survey (dict):      A dict containing the survey data
                            as well as its name and url.

    Returns:
        clean_data (list):  A list containing the clean survey
                            data.
    """
    entries = []
    for report in survey["reports"]:
        if "mouse_repeat" in report.keys():
            files = add_attachments(report,survey["content"])

            for individual in report["mouse_repeat"]:

                data = {
                    "date_trap": parse_to_utc(report["Fecha_y_Hora"]),
                    "kobo_url": survey["kobo_url"],
                    "user": report["_submitted_by"]
                }

                if report["_Registrar_el_sitio_con_GPS_o"] == "celular":
                    data.update({
                        "latitude": str(report["_geolocation"][0]),
                        "longitude": str(report["_geolocation"][1])
                    })
                elif report["_Registrar_el_sitio_con_GPS_o"] == "gps":
                    lat = [(key, value) for key, value in report.items() if key.startswith("Latitud_en_grados_de_ales_de_la_trampa")][0][1]
                    lng = [(key, value) for key, value in report.items() if key.startswith("Longitud_en_grados_d_ales_de_la_trampa")][0][1]

                    data.update({
                        "latitude": lat,
                        "longitude": lng
                    })
                data.update({
                    "clave_posicion_malla": individual["mouse_repeat/v1"]
                })

                # fill with individual info the metadata field
                # the metadata is build as a string, but holds a json
                metadata = "{ \"archivos\": " + files + ", \"caracteristicas\": {"
                for idx,(q,ans) in enumerate(individual.items()):
                    question = q.split("/")[1]
                    field_label = list(
                                        filter(lambda question_label: "name" in question_label and question_label['name'] == question, survey["content"]))
                    field_name = (field_label[0]["label"][0] if "label" in field_label[0].keys() else question) if len(field_label) > 0 else question
                    if not question.startswith("Foto") or question != "c2" or question != "c3":
                        metadata += "\"pregunta_" + str(idx) + "\": { \"nombre\": \"" + field_name + "\", respuesta: \"" + ans + "\"},"

                metadata += "} }"

                data.update({"metadata": metadata})

                if "mouse_repeat/Indique_el_n_mero_de_e_se_le_va_a_colocar" in individual:
                    data.update({
                        "arete": individual["mouse_repeat/Indique_el_n_mero_de_e_se_le_va_a_colocar"]
                    })

                entries.append(data)

    return entries

def clean_kobo_erie_report(survey):
    """
    Returns the desired data for a erie survey.

    Parameters:
        survey (dict):      A dict containing the survey data
                            as well as its name and url.

    Returns:
        clean_data (list):  A list containing the clean survey
                            data.
    """
    entries = []
    for report in survey["reports"]:
        data = {
            "number": report["transecto"],
            "date_transecto": parse_to_utc(report["Fecha_y_Hora"]),
            "kobo_url": survey["kobo_url"],
            "user": report["_submitted_by"]
        }

        try:
            regex_structure = "suma([a-zA-Z_]*)estrutura_vegetacion"
            sum_veg_structure = [(key, value) for key, value in report.items() if re.match(regex_structure,key)][0][1]
        except:
            sum_veg_structure = "0"

        try:
            regex_species = "suma([a-zA-Z_]*)especie_indicadora"
            sum_species = [(key, value) for key, value in report.items() if re.match(regex_species,key)][0][1]
        except:
            sum_species = "0"
        try:
            regex_percentage = "porcentaje([a-zA-Z_]*)"
            percentage = [(key, value) for key, value in report.items() if re.match(regex_percentage,key)][0][1]
        except:
            percentage = "0"

        sum_impact = [(key, value) for key, value in report.items() if key.startswith("suma_impacto")][0][1]

        data.update({
            "sum_vegetation_structure": sum_veg_structure,
            "sum_indicator_species": sum_species,
            "sum_impact": sum_impact,
            "percentage": percentage
        })

        if report["_Registrar_el_sitio_donde_col"] == "celular__recomendado":
            data.update({
                "latitude": str(report["_geolocation"][0]),
                "longitude": str(report["_geolocation"][1])
            })
        elif report["_Registrar_el_sitio_donde_col"] == "gps":
            data.update({
                "latitude": report["Latitud_en_grados_decimales"],
                "longitude": report["Longitud_en_grados_decimales"]
            })

        entries.append(data)

    return entries
