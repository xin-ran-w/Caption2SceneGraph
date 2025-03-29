JSON_SCHEMA = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "instances": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "attributes": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string"
          },
          "dimension": {
            "type": "string"
          },
          "value": {
            "oneOf": [
              {
                "type": "string"
              },
              {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            ]
          }
        },
        "required": ["id", "dimension", "value"]
      }
    },
    "relations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "relation": {
            "type": "string"
          },
          "source": {
            "type": "string"
          },
          "target": {
            "type": "string"
          }
        },
        "required": ["relation", "source", "target"]
      }
    }
  },
  "required": ["instances", "attributes", "relations"]
}

