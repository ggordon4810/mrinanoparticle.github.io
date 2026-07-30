DROP TABLE IF EXISTS relaxivity_measurements;
DROP TABLE IF EXISTS experiments;

CREATE TABLE experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_name TEXT NOT NULL,
    experiment_date TEXT NOT NULL,

    ligand TEXT,
    lipid TEXT,
    ligand_amount_mg REAL,
    lipid_amount_mg REAL,

    solvent TEXT,
    hydration_volume_ml REAL,

    z_average_nm REAL,
    pdi REAL,
    intensity_size_nm REAL,
    volume_size_nm REAL,
    number_size_nm REAL,

    relaxivity REAL,
    r_squared REAL,

    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE relaxivity_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id INTEGER NOT NULL,

    concentration_mm REAL NOT NULL,
    t1_ms REAL NOT NULL,
    r1_per_second REAL,

    FOREIGN KEY (experiment_id)
        REFERENCES experiments(id)
        ON DELETE CASCADE
);
