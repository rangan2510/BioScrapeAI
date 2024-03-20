# boilerplate
from flask import Flask, jsonify, request

app = Flask(__name__)

# Dummy data for testing
data = [
    {"id": 1, "name": "John"},
    {"id": 2, "name": "Jane"}
]

# Route to get all data
@app.route('/api/data', methods=['GET'])
def get_all_data():
    return jsonify(data)

# Route to get data by id
@app.route('/api/data/<int:id>', methods=['GET'])
def get_data_by_id(id):
    result = [item for item in data if item['id'] == id]
    if len(result) == 0:
        return jsonify({'error': 'Data not found'}), 404
    return jsonify(result[0])

# Route to add new data
@app.route('/api/data', methods=['POST'])
def add_data():
    new_data = request.json
    if 'id' not in new_data or 'name' not in new_data:
        return jsonify({'error': 'Missing data'}), 400
    data.append(new_data)
    return jsonify({'message': 'Data added successfully'}), 201

# Route to update data by id
@app.route('/api/data/<int:id>', methods=['PUT'])
def update_data(id):
    update_data = request.json
    for item in data:
        if item['id'] == id:
            item.update(update_data)
            return jsonify({'message': 'Data updated successfully'})
    return jsonify({'error': 'Data not found'}), 404

# Route to delete data by id
@app.route('/api/data/<int:id>', methods=['DELETE'])
def delete_data(id):
    global data
    data = [item for item in data if item['id'] != id]
    return jsonify({'message': 'Data deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
