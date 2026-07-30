#CHAT GPT helped me understand errors that occured when attempting to run this function
from flask import Flask, flash, redirect, render_template, request, url_for

from calculations import analyze_dls, calculate_relaxivity
from helpers import (
    fetch_all,
    fetch_one,
    get_db_connection,
    initialize_database,
    parse_number_list,
    parse_optional_float,
    parse_required_float,
)


app = Flask(__name__)

# Flask uses this key to securely store flash messages.
# Replace this with your own random string before submitting the project.
app.config["SECRET_KEY"] = "replace-this-with-a-random-secret-key"


# Create the database tables when the application starts.
initialize_database()


@app.route("/")
def index():
    """
    Display the dashboard and the five most recent experiments.
    """

    experiments = fetch_all(
        """
        SELECT *
        FROM experiments
        ORDER BY date_created DESC
        LIMIT 5
        """
    )

    return render_template(
        "index.html",
        experiments=experiments
    )

@app.route("/experiments")
def experiments():
    """
    Display all saved experiments.
    """

    experiment_records = fetch_all(
        """
        SELECT *
        FROM experiments
        ORDER BY date_created DESC
        """
    )

    return render_template(
        "experiments.html",
        experiments=experiment_records
    )


@app.route("/experiments/new", methods=["GET", "POST"])
def new_experiment():
    """
    Display the new experiment form and save submitted experiments.
    """

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        sample_type = request.form.get("sample_type", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Please enter an experiment name.", "error")

            return render_template("new_experiment.html")

        if len(name) > 150:
            flash(
                "The experiment name must be 150 characters or fewer.",
                "error"
            )

            return render_template("new_experiment.html")

        if len(description) > 2000:
            flash(
                "The experiment description must be 2,000 characters or fewer.",
                "error"
            )

            return render_template("new_experiment.html")

        connection = get_db_connection()

        try:
            cursor = connection.execute(
                """
                INSERT INTO experiments (
                    name,
                    sample_type,
                    description
                )
                VALUES (?, ?, ?)
                """,
                (
                    name,
                    sample_type or None,
                    description or None
                )
            )

            connection.commit()

            experiment_id = cursor.lastrowid

        finally:
            connection.close()

        flash("Experiment created successfully.", "success")

        return redirect(
            url_for(
                "experiment_detail",
                experiment_id=experiment_id
            )
        )

    return render_template("new_experiment.html")

@app.route("/experiments/<int:experiment_id>")
def experiment_detail(experiment_id):
    """
    Display one experiment and its saved relaxivity and DLS results.
    """

    experiment = fetch_one(
        """
        SELECT *
        FROM experiments
        WHERE id = ?
        """,
        (experiment_id,)
    )

    if experiment is None:
        return render_template(
            "error.html",
            error_code=404,
            error_message="The requested experiment could not be found."
        ), 404

    relaxivity_results = fetch_all(
        """
        SELECT *
        FROM relaxivity_results
        WHERE experiment_id = ?
        ORDER BY date_created DESC
        """,
        (experiment_id,)
    )

    dls_results = fetch_all(
        """
        SELECT *
        FROM dls_results
        WHERE experiment_id = ?
        ORDER BY date_created DESC
        """,
        (experiment_id,)
    )

    return render_template(
        "experiment_detail.html",
        experiment=experiment,
        relaxivity_results=relaxivity_results,
        dls_results=dls_results
    )


@app.route("/relaxivity", methods=["GET", "POST"])
def relaxivity():
    results = None
    error = None

    if request.method == "POST":
        try:
            # Get every input with these names from the form.
            concentration_values = request.form.getlist("concentration")
            t1_values = request.form.getlist("t1")

            # Convert each concentration entry into a float.
            concentrations = [
                float(value.strip())
                for value in concentration_values
                if value and value.strip()
            ]

            # Convert each T1 entry into a float.
            t1_times_ms = [
                float(value.strip())
                for value in t1_values
                if value and value.strip()
            ]

            if len(concentrations) != len(t1_times_ms):
                raise ValueError(
                    "Each concentration must have a corresponding T1 value."
                )

            if len(concentrations) < 2:
                raise ValueError(
                    "Enter at least two measurements."
                )

            results = calculate_relaxivity(
                concentrations,
                t1_times_ms
            )

        except ValueError as exc:
            error = str(exc)

    return render_template(
        "relaxivity.html",
        results=results,
        error=error
    )


def save_relaxivity_result(experiment_id, results):
    """
    Save a relaxivity result and its individual measurements.
    """

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO relaxivity_results (
                experiment_id,
                relaxivity,
                intercept,
                r_squared
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                experiment_id,
                float(results["relaxivity"]),
                float(results["intercept"]),
                float(results["r_squared"])
            )
        )

        result_id = cursor.lastrowid

        for measurement in results["measurements"]:
            connection.execute(
                """
                INSERT INTO relaxivity_measurements (
                    relaxivity_result_id,
                    concentration,
                    t1,
                    r1
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    result_id,
                    float(measurement["concentration"]),
                    float(measurement["t1"]),
                    float(measurement["r1"])
                )
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

@app.route("/dls", methods=["GET", "POST"])
def dls():
    """
    Analyze DLS size measurements and polydispersity.

    A result is saved to the database when the user selects an experiment.
    """

    experiment_records = fetch_all(
        """
        SELECT id, name
        FROM experiments
        ORDER BY date_created DESC
        """
    )

    selected_experiment_id = request.args.get(
        "experiment_id",
        type=int
    )

    results = None

    z_average_nm = None
    pdi = None
    intensity_size_nm = None
    volume_size_nm = None
    number_size_nm = None

    if request.method == "POST":
        selected_experiment_id = request.form.get(
            "experiment_id",
            type=int
        )

        try:
            z_average_nm = parse_required_float(
                request.form.get("z_average_nm"),
                "Z-average"
            )

            pdi = parse_required_float(
                request.form.get("pdi"),
                "PDI"
            )

            intensity_size_nm = parse_optional_float(
                request.form.get("intensity_size_nm"),
                "Intensity size"
            )

            volume_size_nm = parse_optional_float(
                request.form.get("volume_size_nm"),
                "Volume size"
            )

            number_size_nm = parse_optional_float(
                request.form.get("number_size_nm"),
                "Number size"
            )

            results = analyze_dls(
                z_average_nm=z_average_nm,
                pdi=pdi,
                intensity_size_nm=intensity_size_nm,
                volume_size_nm=volume_size_nm,
                number_size_nm=number_size_nm
            )

            if selected_experiment_id is not None:
                experiment = fetch_one(
                    """
                    SELECT id
                    FROM experiments
                    WHERE id = ?
                    """,
                    (selected_experiment_id,)
                )

                if experiment is None:
                    raise ValueError(
                        "The selected experiment does not exist."
                    )

                save_dls_result(
                    selected_experiment_id,
                    z_average_nm,
                    pdi,
                    intensity_size_nm,
                    volume_size_nm,
                    number_size_nm,
                    results
                )

                flash(
                    "DLS analysis calculated and saved.",
                    "success"
                )

            else:
                flash(
                    "DLS analysis calculated. Select an experiment "
                    "to save future results.",
                    "success"
                )

        except ValueError as error:
            flash(str(error), "error")

            results = None

    return render_template(
        "dls.html",
        experiments=experiment_records,
        selected_experiment_id=selected_experiment_id,
        results=results,
        z_average_nm=z_average_nm,
        pdi=pdi,
        intensity_size_nm=intensity_size_nm,
        volume_size_nm=volume_size_nm,
        number_size_nm=number_size_nm
    )


def save_dls_result(
    experiment_id,
    z_average_nm,
    pdi,
    intensity_size_nm,
    volume_size_nm,
    number_size_nm,
    results
):
    """
    Save a DLS analysis result to the database.
    """

    connection = get_db_connection()

    try:
        connection.execute(
            """
            INSERT INTO dls_results (
                experiment_id,
                z_average_nm,
                pdi,
                intensity_size_nm,
                volume_size_nm,
                number_size_nm,
                recommended_value,
                interpretation
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                experiment_id,
                z_average_nm,
                pdi,
                intensity_size_nm,
                volume_size_nm,
                number_size_nm,
                results["recommended_value"],
                results["interpretation"]
            )
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

@app.errorhandler(404)
def page_not_found(error):
    """
    Display a custom page when a route cannot be found.
    """

    return render_template(
        "error.html",
        error_code=404,
        error_message="The page you requested could not be found."
    ), 404


@app.errorhandler(500)
def internal_server_error(error):
    """
    Display a custom page when an unexpected server error occurs.
    """

    app.logger.exception(error)

    return render_template(
        "error.html",
        error_code=500,
        error_message=(
            "An unexpected server error occurred. Please try again."
        )
    ), 500

if __name__ == "__main__":
    app.run(debug=True)
