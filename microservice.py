import json
import os
import random
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_PATH = os.path.join(os.path.dirname(__file__), "exercises.json")

with open(DATA_PATH, encoding="utf-8") as f:
    EXERCISES = json.load(f)

SUPPORTED_DAYS = [1, 7, 14]

EQUIPMENT_GROUPS = {
    "none": ["None", "None (optional weight)"],
    "dumbbells": ["None", "None (optional weight)", "Dumbbell", "Dumbbells",
                  "Dumbbells, Bench", "Bench or Chair", "Chair or Bench",
                  "Resistance Band"],
    "full": ["None", "None (optional weight)", "Dumbbell", "Dumbbells",
             "Dumbbells, Bench", "Bench or Chair", "Chair or Bench",
             "Resistance Band"]
}

MUSCLE_ROTATION = ["Legs", "Back", "Chest", "Shoulders", "Arms", "Core"]


def filter_exercises(difficulty, equipment_key):
    allowed_equipment = EQUIPMENT_GROUPS.get(equipment_key.lower(),
                                             EQUIPMENT_GROUPS["none"])
    return [
        e for e in EXERCISES
        if e["difficulty"].lower() == difficulty.lower()
        and e["equipment"] in allowed_equipment
    ]


def build_day(day_number, muscle_group, pool):
    candidates = [e for e in pool if e["muscle_group"] == muscle_group]
    if not candidates:
        candidates = pool
    selected = random.sample(candidates, min(3, len(candidates)))
    return {
        "day": day_number,
        "muscle_focus": muscle_group,
        "exercises": [
            {
                "id": e["id"],
                "name": e["name"],
                "muscle_group": e["muscle_group"],
                "difficulty": e["difficulty"],
                "reps_sets": e["reps_sets"],
                "equipment": e["equipment"]
            }
            for e in selected
        ]
    }


@app.route("/plan", methods=["POST"])
def get_plan():
    body = request.get_json(silent=True)

    if not body:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    difficulty = body.get("difficulty", "").strip()
    equipment = body.get("equipment", "").strip()
    days = body.get("days", 1)

    # Validate difficulty
    if difficulty.lower() not in ["beginner", "intermediate", "advanced"]:
        return jsonify({
            "error": "Invalid difficulty. Supported values: 'Beginner', 'Intermediate', 'Advanced'."
        }), 400

    # Validate equipment
    if equipment.lower() not in EQUIPMENT_GROUPS:
        return jsonify({
            "error": "Invalid equipment. Supported values: 'none', 'dumbbells', 'full'."
        }), 400

    # Validate days
    if days not in SUPPORTED_DAYS:
        return jsonify({
            "error": f"Invalid days value. Supported values: {SUPPORTED_DAYS}."
        }), 400

    pool = filter_exercises(difficulty, equipment)

    if not pool:
        return jsonify({
            "error": "No exercises found matching the given difficulty and equipment."
        }), 404

    plan = []
    for day_number in range(1, days + 1):
        muscle = MUSCLE_ROTATION[(day_number - 1) % len(MUSCLE_ROTATION)]
        plan.append(build_day(day_number, muscle, pool))

    return jsonify({
        "difficulty": difficulty,
        "equipment": equipment,
        "days": days,
        "plan": plan
    }), 200


if __name__ == "__main__":
    print("Workout Plan Microservice running on http://localhost:5004")
    app.run(port=5004)
