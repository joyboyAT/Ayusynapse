#!/usr/bin/env python3
"""
FHIR Validator - Validates FHIR bundles against HL7 FHIR specification
"""

import json
import sys
import logging
from typing import Dict, List, Any, Optional
from jsonschema import validate, ValidationError
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class FHIRValidator:
    """Validates FHIR resources against HL7 FHIR specification"""
    
    def __init__(self):
        # Simplified FHIR schemas for core resources
        self.fhir_schemas = {
            "Bundle": {
                "type": "object",
                "required": ["resourceType", "type", "entry"],
                "properties": {
                    "resourceType": {"type": "string", "enum": ["Bundle"]},
                    "type": {"type": "string", "enum": ["collection", "searchset", "history", "document", "message", "transaction", "transaction-response", "batch", "batch-response"]},
                    "entry": {"type": "array", "items": {"$ref": "#/definitions/BundleEntry"}}
                },
                "definitions": {
                    "BundleEntry": {
                        "type": "object",
                        "required": ["resource"],
                        "properties": {
                            "resource": {"$ref": "#/definitions/FHIRResource"}
                        }
                    },
                    "FHIRResource": {
                        "type": "object",
                        "required": ["resourceType"],
                        "properties": {
                            "resourceType": {"type": "string"}
                        }
                    }
                }
            },
            "Condition": {
                "type": "object",
                "required": ["resourceType", "code"],
                "properties": {
                    "resourceType": {"type": "string", "enum": ["Condition"]},
                    "code": {"$ref": "#/definitions/CodeableConcept"},
                    "subject": {"$ref": "#/definitions/Reference"},
                    "clinicalStatus": {"$ref": "#/definitions/CodeableConcept"},
                    "verificationStatus": {"$ref": "#/definitions/CodeableConcept"},
                    "category": {"type": "array", "items": {"$ref": "#/definitions/CodeableConcept"}},
                    "onsetDateTime": {"type": "string", "format": "date-time"},
                    "recordedDate": {"type": "string", "format": "date-time"}
                }
            },
            "Observation": {
                "type": "object",
                "required": ["resourceType", "status", "code"],
                "properties": {
                    "resourceType": {"type": "string", "enum": ["Observation"]},
                    "status": {"type": "string", "enum": ["registered", "preliminary", "final", "amended", "corrected", "cancelled", "entered-in-error", "unknown"]},
                    "code": {"$ref": "#/definitions/CodeableConcept"},
                    "subject": {"$ref": "#/definitions/Reference"},
                    "category": {"type": "array", "items": {"$ref": "#/definitions/CodeableConcept"}},
                    "valueCodeableConcept": {"$ref": "#/definitions/CodeableConcept"},
                    "valueQuantity": {"$ref": "#/definitions/Quantity"},
                    "effectiveDateTime": {"type": "string", "format": "date-time"},
                    "issued": {"type": "string", "format": "date-time"},
                    "performer": {"type": "array", "items": {"$ref": "#/definitions/Reference"}}
                }
            },
            "Patient": {
                "type": "object",
                "required": ["resourceType"],
                "properties": {
                    "resourceType": {"type": "string", "enum": ["Patient"]},
                    "identifier": {"type": "array", "items": {"$ref": "#/definitions/Identifier"}},
                    "active": {"type": "boolean"},
                    "name": {"type": "array", "items": {"$ref": "#/definitions/HumanName"}},
                    "gender": {"type": "string", "enum": ["male", "female", "other", "unknown"]},
                    "birthDate": {"type": "string", "format": "date"}
                }
            },
            "MedicationRequest": {
                "type": "object",
                "required": ["resourceType", "medicationCodeableConcept"],
                "properties": {
                    "resourceType": {"type": "string", "enum": ["MedicationRequest"]},
                    "medicationCodeableConcept": {"$ref": "#/definitions/CodeableConcept"},
                    "subject": {"$ref": "#/definitions/Reference"},
                    "dosageInstruction": {"type": "array", "items": {"$ref": "#/definitions/Dosage"}}
                }
            }
        }
        
        # Common FHIR data types
        self.common_definitions = {
            "CodeableConcept": {
                "type": "object",
                "properties": {
                    "coding": {"type": "array", "items": {"$ref": "#/definitions/Coding"}},
                    "text": {"type": "string"}
                }
            },
            "Coding": {
                "type": "object",
                "properties": {
                    "system": {"type": "string", "format": "uri"},
                    "code": {"type": "string"},
                    "display": {"type": "string"}
                }
            },
            "Reference": {
                "type": "object",
                "properties": {
                    "reference": {"type": "string"},
                    "display": {"type": "string"}
                }
            },
            "Identifier": {
                "type": "object",
                "properties": {
                    "system": {"type": "string", "format": "uri"},
                    "value": {"type": "string"}
                }
            },
            "HumanName": {
                "type": "object",
                "properties": {
                    "use": {"type": "string", "enum": ["usual", "official", "temp", "nickname", "anonymous", "old", "maiden"]},
                    "text": {"type": "string"}
                }
            },
            "Quantity": {
                "type": "object",
                "properties": {
                    "value": {"type": "number"},
                    "unit": {"type": "string"},
                    "system": {"type": "string", "format": "uri"},
                    "code": {"type": "string"}
                }
            },
            "Dosage": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                }
            }
        }
    
    def validate_bundle(self, bundle_data: Dict) -> bool:
        """
        Validate a FHIR Bundle against the FHIR specification
        
        Args:
            bundle_data: The FHIR bundle to validate
            
        Returns:
            bool: True if valid, False if invalid
        """
        try:
            # Check if it's a bundle
            if not isinstance(bundle_data, dict):
                logger.error("❌ Invalid: Bundle must be a JSON object")
                return False
            
            if bundle_data.get("resourceType") != "Bundle":
                logger.error("❌ Invalid: Missing or incorrect resourceType (must be 'Bundle')")
                return False
            
            # Create a complete schema with all definitions
            bundle_schema = {
                "type": "object",
                "required": ["resourceType", "type", "entry"],
                "properties": {
                    "resourceType": {"type": "string", "enum": ["Bundle"]},
                    "type": {"type": "string", "enum": ["collection", "searchset", "history", "document", "message", "transaction", "transaction-response", "batch", "batch-response"]},
                    "entry": {"type": "array", "items": {"$ref": "#/definitions/BundleEntry"}}
                },
                "definitions": {
                    "BundleEntry": {
                        "type": "object",
                        "required": ["resource"],
                        "properties": {
                            "resource": {"$ref": "#/definitions/FHIRResource"}
                        }
                    },
                    "FHIRResource": {
                        "type": "object",
                        "required": ["resourceType"],
                        "properties": {
                            "resourceType": {"type": "string"}
                        }
                    },
                    **self.common_definitions,
                    **{k: v for k, v in self.fhir_schemas.items() if k != "Bundle"}
                }
            }
            
            # Validate the bundle structure
            validate(instance=bundle_data, schema=bundle_schema)
            
            # Validate each resource in the bundle
            if "entry" in bundle_data:
                for i, entry in enumerate(bundle_data["entry"]):
                    if "resource" in entry:
                        resource = entry["resource"]
                        resource_type = resource.get("resourceType")
                        
                        if resource_type in self.fhir_schemas:
                            # Create a schema for this specific resource type
                            resource_schema = {
                                "type": "object",
                                "definitions": {
                                    **self.common_definitions,
                                    **{k: v for k, v in self.fhir_schemas.items() if k != "Bundle"}
                                },
                                **self.fhir_schemas[resource_type]
                            }
                            try:
                                validate(instance=resource, schema=resource_schema)
                            except ValidationError as e:
                                logger.error(f"❌ Invalid resource {i+1} ({resource_type}): {e.message}")
                                logger.error(f"   Path: {' -> '.join(str(p) for p in e.path)}")
                                return False
                        else:
                            logger.warning(f"⚠️  Unknown resource type: {resource_type}")
            
            logger.info("✅ Bundle is valid")
            return True
            
        except ValidationError as e:
            logger.error(f"❌ Validation error: {e.message}")
            logger.error(f"   Path: {' -> '.join(str(p) for p in e.path)}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error during validation: {e}")
            return False
    
    def validate_resource(self, resource_data: Dict, resource_type: str) -> bool:
        """
        Validate a single FHIR resource
        
        Args:
            resource_data: The FHIR resource to validate
            resource_type: The expected resource type
            
        Returns:
            bool: True if valid, False if invalid
        """
        try:
            if resource_type not in self.fhir_schemas:
                logger.error(f"❌ Unknown resource type: {resource_type}")
                return False
            
            validate(instance=resource_data, schema=self.fhir_schemas[resource_type])
            logger.info(f"✅ {resource_type} resource is valid")
            return True
            
        except ValidationError as e:
            logger.error(f"❌ {resource_type} validation error: {e.message}")
            logger.error(f"   Path: {' -> '.join(str(p) for p in e.path)}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error validating {resource_type}: {e}")
            return False
    
    def load_and_validate_file(self, file_path: str) -> bool:
        """
        Load and validate a FHIR bundle from a JSON file
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            bool: True if valid, False if invalid
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                bundle_data = json.load(f)
            
            logger.info(f"Validating file: {file_path}")
            return self.validate_bundle(bundle_data)
            
        except FileNotFoundError:
            logger.error(f"❌ File not found: {file_path}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in file {file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error reading file {file_path}: {e}")
            return False

def create_bundle_example():
    """Create a minimal valid FHIR bundle example"""
    bundle_example = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Condition",
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "44054006",
                                "display": "Diabetes mellitus"
                            }
                        ]
                    }
                }
            }
        ]
    }
    
    with open('bundle_example.json', 'w') as f:
        json.dump(bundle_example, f, indent=2)
    
    logger.info("✅ Created bundle_example.json")

def main():
    """Main function to run the validator"""
    if len(sys.argv) > 1:
        # Validate file provided as command line argument
        file_path = sys.argv[1]
        validator = FHIRValidator()
        success = validator.load_and_validate_file(file_path)
        sys.exit(0 if success else 1)
    else:
        # Run tests
        validator = FHIRValidator()
        
        print("=== FHIR Validator Tests ===")
        
        # Test 1: Empty object (should fail)
        print("\n1. Testing empty object:")
        result1 = validator.validate_bundle({})
        print(f"Result: {'✅ PASS' if not result1 else '❌ FAIL'}")
        
        # Test 2: Invalid bundle (missing required fields)
        print("\n2. Testing invalid bundle:")
        invalid_bundle = {"resourceType": "Bundle"}
        result2 = validator.validate_bundle(invalid_bundle)
        print(f"Result: {'✅ PASS' if not result2 else '❌ FAIL'}")
        
        # Test 3: Valid bundle
        print("\n3. Testing valid bundle:")
        valid_bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Condition",
                        "code": {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "code": "44054006",
                                    "display": "Diabetes mellitus"
                                }
                            ]
                        }
                    }
                }
            ]
        }
        result3 = validator.validate_bundle(valid_bundle)
        print(f"Result: {'✅ PASS' if result3 else '❌ FAIL'}")
        
        # Create example file
        print("\n4. Creating bundle_example.json:")
        create_bundle_example()

if __name__ == "__main__":
    main()
