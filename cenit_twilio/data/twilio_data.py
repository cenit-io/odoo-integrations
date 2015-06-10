twilio_data = {
  "name": "Twilio API Integration",
  "shared_version": "1.0.0",
  "description": "Twilio API Integration",
  "data": {
    "name": "Twilio API Integration",
    "flows": [
      {
        "name": "Send SMS with Twilio API",
        "active": True,
        "discard_events": False,
        "data_type_scope": "Event source",
        "last_trigger_timestamps": "2015-04-24 15:47:50 UTC",
        "event": {
          "_reference": True,
          "name": "Communication | SMS on created_at"
        },
        "translator": {
          "_reference": True,
          "name": "SMS to Twilio API"
        },
        "webhook": {
          "_reference": True,
          "name": "Twilio API | Send SMS"
        }
      }
    ],
    "connection_roles": [
      {
        "name": "Twilio API Rol",
        "webhooks": [
          {
            "_reference": True,
            "name": "Twilio API | Send SMS"
          }
        ],
        "connections": [
          {
            "_reference": True,
            "name": "Twilio API Conection"
          }
        ]
      }
    ],
    "translators": [
      {
        "name": "SMS to Twilio API",
        "type": "Export",
        "style": "ruby",
        "mime_type": "application/x-www-form-urlencoded",
        "bulk_source": False,
        "transformation": "\"Body=#{source.message}&To=#{source.phone}&From=#{source.from}\"",
        "source_data_type": {
          "_reference": True,
          "name": "Sms",
          "schema": {
            "_reference": True,
            "uri": "sms.json",
            "library": {
              "_reference": True,
              "name": "Communication"
            }
          }
        }
      }
    ],
    "events": [
      {
        "name": "Communication | SMS on created_at",
        "_type": "Setup::Observer",
        "triggers": "{\"created_at\":{\"0\":{\"o\":\"_not_null\",\"v\":[\"\",\"\",\"\"]}}}",
        "data_type": {
          "_reference": True,
          "name": "Sms",
          "schema": {
            "_reference": True,
            "uri": "sms.json",
            "library": {
              "_reference": True,
              "name": "Communication"
            }
          }
        }
      }
    ],
    "connections": [
      {
        "name": "Twilio API Conection",
        "url": "https://api.twilio.com/2010-04-01/Accounts/{{account_sid}}",
        "headers": [
          {
            "key": "Accept-Charset:",
            "value": "utf-8"
          },
          {
            "key": "Accept",
            "value": "application/json"
          },
          {
            "key": "Authorization",
            "value": "Basic {% base64 (account_sid + ':'  + auth_token) %}"
          }
        ],
        "template_parameters": [
          {
            "key": "auth_token"
          },
          {
            "key": "account_sid"
          }
        ]
      }
    ],
    "webhooks": [
      {
        "name": "Twilio API | Send SMS",
        "path": "Messages.json",
        "purpose": "send",
        "method": "post"
      }
    ],
    "libraries": [
      {
        "name": "Communication",
        "schemas": [
          {
            "uri": "sms.json",
            "schema": "{\n  \"title\": \"SMS\",\n  \"type\": \"object\",\n  \"properties\": {\n    \"id\": {\n      \"type\": \"string\"\n    },\n    \"from\": {\n      \"type\": \"string\"\n    },\n    \"message\": {\n      \"type\": \"string\"\n    },\n    \"phone\": {\n      \"type\": \"string\"\n    }\n  }\n}",
            "library": {
              "_reference": True,
              "name": "Communication"
            }
          }
        ]
      }
    ]
  },
  "pull_parameters": [
    {
      "type": "connection",
      "name": "Twilio API Conection",
      "label": "Account SID",
      "property": "template_parameters",
      "key": "account_sid",
      "parameter": "On connection 'Twilio API Conection' template parameter 'account_sid'"
    },
    {
      "type": "connection",
      "name": "Twilio API Conection",
      "label": "Auth Token",
      "property": "template_parameters",
      "key": "auth_token",
      "parameter": "On connection 'Twilio API Conection' template parameter 'auth_token'"
    }
  ]
}
