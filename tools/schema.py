"""Canonical CORE schema.

One place to change when Siegen renames a column. Everything else - the importer,
the search index and the layouts - is driven from here.
"""

# (excel_header, toml_key, kind, label)
#   kind: "str"  -> TOML string
#         "list" -> TOML array, semicolon-separated in the sheet
#   label: heading used on the entry page
FIELDS = [
    ("Corpus Version",                                            "corpus_version",           "str",  "Corpus Version"),
    ("Name",                                                      "name",                     "str",  "Name"),
    ("Short Description",                                         "short_description",        "str",  "Short Description"),
    ("Online Publication Year",                                   "publication_year",         "str",  "Publication Year"),
    ("Publication Type",                                          "publication_type",         "str",  "Publication Type"),
    ("Reference",                                                 "reference",                "str",  "Reference"),
    ("Tags",                                                      "tags",                     "list", "Tags"),
    ("Target Group of People –Target Group",                      "target_group",             "list", "Type of Relationship"),
    ("Target Group of People – Additional Specification",         "target_group_details",     "str",  "Additional Specification"),
    ("Aim and Designers' Intention",                              "aim",                      "str",  "Aim and Designer's Intention"),
    ("Psychological Constructs with reference",                   "psych_constructs",         "str",  "Psychological Constructs with Reference"),
    ("Psychological Constructs with reference – References",      "psych_constructs_refs",    "str",  "Psychological Constructs – References"),
    ("Constructs and Terms Used Without Reference",               "constructs_without_ref",   "str",  "Constructs and Terms Without Reference"),
    ("Design – Strategy ",                                        "design_strategy",          "list", "Design Strategy"),
    ("Design – Role of Technology",                               "design_role",              "str",  "Role of Technology"),
    ("Design – Form factor",                                      "design_form_factor",       "str",  "Form Factor"),
    ("Design – Symmetry of Interaction Devices",                  "design_symmetry",          "str",  "Symmetry of Interaction Devices"),
    ("Design – Input Modalities",                                 "design_input",             "list", "Input Modalities"),
    ("Design  – Output Modalities",                               "design_output",            "list", "Output Modalities"),
    ("Design – Synchronicity of Interaction",                     "design_synchronicity",     "str",  "Synchronicity of Interaction"),
    ("Evaluation ",                                               "evaluation",               "str",  "Evaluation"),
    ("Evaluation – Methodology",                                  "eval_methodology",         "str",  "Evaluation Methodology"),
    ("Evaluation – Type of Study",                                "eval_study_type",          "str",  "Type of Study"),
    ("Evaluation – Experimental Design",                          "eval_experimental_design", "str",  "Experimental Design"),
    ("Evaluation – Duration of Data Collection",                  "eval_duration",            "str",  "Duration of Data Collection"),
    ("Evaluation _ Number of Participants  (N)",                  "eval_participants_n",      "str",  "Number of Participants"),
    ("Evaluation –  Selected Participants",                       "eval_participants",        "str",  "Selected Participants"),
    ("Evaluation –    Selection Criteria of Participants",        "eval_selection_criteria",  "str",  "Selection Criteria of Participants"),
    ("Evaluation –  Measurements and instruments (with reference)", "eval_measurements",      "str",  "Measurements and Instruments"),
    ("Evaluation –  Measurements and instruments – References",   "eval_measurements_refs",   "str",  "Measurements and Instruments – References"),
    ("Ethical issues and concerns",                               "ethics_concerns",          "str",  "Ethical Concerns"),
    ("Consideration of Ethical Issues in Design Decisions",       "ethics_in_design",         "str",  "Consideration of Ethical Issues in Design Decisions"),
    ("Ethical Issues Addressed",                                  "ethics_addressed",         "str",  "Ethical Issues Addressed"),
]

# Column A of the sheet carries Siegen's NEW marker; it is not corpus data.
MARKER_COLUMN = "Unnamed: 0"

KEYS = [k for _, k, _, _ in FIELDS]
LIST_KEYS = [k for _, k, kind, _ in FIELDS if kind == "list"]


# --- keyword normalisation -------------------------------------------------
# Case variants, typos and plural drift in the sheet's Tags column. Merges only;
# no tag is dropped from an entry. Reviewed and approved 2026-09.
TAG_MERGES = {
    "Object": "Object(s)",
    "Domestic Object": "Domestic object",
    "Domestic object(s)": "Domestic object",
    "IoT-enabled domestic object(s)s": "IoT-enabled domestic object(s)",
    "IoT-enabled domestic object": "IoT-enabled domestic object(s)",
    "IoT-enabled workplace": "IoT-enabled workplace object(s)",
    "Artificial intelligence (AI)": "Artificial Intelligence (AI)",
    "Artificial Intelligenc (AI)": "Artificial Intelligence (AI)",
    "AI": "Artificial Intelligence (AI)",
    "VR": "Virtual Reality (VR)",
    "VR (Virtual Reality)": "Virtual Reality (VR)",
    "AR (Augmented Reality)": "Augmented Reality (AR)",
    "Tangible Interaction": "Tangible interaction",
    "Tea/Coffee": "Tea/coffee",
    "Picture Frame": "Picture frame",
    "Telepresence  system": "Telepresence system",
    "Natural Language Processing": "Natural language processing",
    "Human food interaction": "Human-food interaction",
    "Virtual Pet": "Virtual pet",
    "Light Panels": "Light panels",
    "Smartphone Alarm": "Smartphone alarm",
    "Remote Brainstorming Session": "Remote brainstorming session",
    "Toobox": "Toolbox",
}

# Cells where a missing semicolon fused two tags into one.
TAG_SPLITS = {
    "Object(s) Tea/coffee": ["Object(s)", "Tea/coffee"],
    "Domestic object: Application": ["Domestic object", "Application"],
}

# Deliberately left alone (reviewed 2026-09): 'Wearable – accessory',
# 'Augmented smartphone/handheld device', 'Messaging (already existing
# applications)', 'Plush toy', 'Lighting' / 'Lamp' / 'Light panels'.


def normalise_tags(raw):
    """Sheet cell -> ordered list of canonical tags, duplicates removed."""
    out = []
    for part in str(raw).split(";"):
        part = " ".join(part.split())
        if not part:
            continue
        for tag in TAG_SPLITS.get(part, [part]):
            tag = TAG_MERGES.get(tag, tag)
            if tag not in out:
                out.append(tag)
    return out
