#!/usr/bin/env python3
"""
FHIR Storage Module - Dedicated module for storing FHIR bundles to HAPI FHIR server
"""

import json
import requests
import logging
import time
from typing import Dict, Optional, List
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class FHIRStorage:
    """Dedicated class for FHIR bundle storage operations"""
    
    def __init__(self, base_url: str = "http://hapi.fhir.org/baseR4"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json'
        })
        
        # Test connection on initialization
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test connection to FHIR server"""
        try:
            response = self.session.get(f"{self.base_url}/metadata")
            if response.status_code == 200:
                logger.info(f"✅ Connected to FHIR server: {self.base_url}")
                return True
            else:
                logger.error(f"❌ Failed to connect to FHIR server: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    def store_bundle(self, bundle: Dict, max_retries: int = 3, retry_delay: float = 1.0) -> Dict:
        """
        Store a FHIR bundle to the HAPI FHIR server with enhanced error handling
        
        Args:
            bundle: FHIR bundle to store
            max_retries: Maximum number of retry attempts for server errors
            retry_delay: Delay between retries in seconds
            
        Returns:
            Dict containing:
                - success: bool
                - resource_id: str (if successful)
                - status: str
                - message: str
                - response_data: dict (full server response)
        """
        for attempt in range(max_retries + 1):
            try:
                # Validate bundle structure
                if not self._validate_bundle(bundle):
                    logger.error("❌ Bundle validation failed - invalid structure")
                    return {
                        'success': False,
                        'resource_id': None,
                        'status': 'validation_failed',
                        'message': 'Invalid bundle structure',
                        'response_data': None
                    }
                
                # Send POST request to /Bundle endpoint
                url = f"{self.base_url}/Bundle"
                logger.info(f"📤 Attempting to store bundle (attempt {attempt + 1}/{max_retries + 1})")
                response = self.session.post(url, json=bundle)
                
                # Handle different HTTP status codes
                if response.status_code in [201, 200]:
                    response_data = response.json()
                    resource_id = response_data.get('id')
                    
                    logger.info(f"✅ Successfully stored bundle with ID: {resource_id}")
                    
                    return {
                        'success': True,
                        'resource_id': resource_id,
                        'status': 'stored',
                        'message': f'Bundle stored successfully with ID: {resource_id}',
                        'response_data': response_data
                    }
                
                elif response.status_code == 400:
                    # Bad Request - validation error
                    logger.error(f"❌ Validation error (400): {response.text}")
                    try:
                        error_data = response.json()
                        error_message = error_data.get('diagnostics', response.text)
                    except:
                        error_message = response.text
                    
                    return {
                        'success': False,
                        'resource_id': None,
                        'status': 'validation_error',
                        'message': f'Bundle validation failed: {error_message}',
                        'response_data': {'error': response.text, 'status_code': 400}
                    }
                
                elif response.status_code == 413:
                    # Request Entity Too Large
                    logger.error(f"❌ Bundle too large (413): {response.text}")
                    return {
                        'success': False,
                        'resource_id': None,
                        'status': 'too_large',
                        'message': 'Bundle size exceeds server limits',
                        'response_data': {'error': response.text, 'status_code': 413}
                    }
                
                elif response.status_code in [500, 502, 503, 504]:
                    # Server errors - retry
                    if attempt < max_retries:
                        logger.warning(f"⚠️  Server error {response.status_code} (attempt {attempt + 1}/{max_retries + 1})")
                        logger.warning(f"Response: {response.text}")
                        logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        logger.error(f"❌ Server error after {max_retries + 1} attempts: {response.status_code}")
                        logger.error(f"Final response: {response.text}")
                        return {
                            'success': False,
                            'resource_id': None,
                            'status': 'server_error',
                            'message': f'Server error after {max_retries + 1} attempts: {response.status_code}',
                            'response_data': {'error': response.text, 'status_code': response.status_code}
                        }
                
                else:
                    # Other HTTP errors
                    logger.error(f"❌ HTTP error {response.status_code}: {response.text}")
                    return {
                        'success': False,
                        'resource_id': None,
                        'status': 'http_error',
                        'message': f'HTTP error {response.status_code}: {response.text}',
                        'response_data': {'error': response.text, 'status_code': response.status_code}
                    }
                
            except requests.exceptions.ConnectionError as e:
                logger.error(f"❌ Connection error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                if attempt < max_retries:
                    logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    return {
                        'success': False,
                        'resource_id': None,
                        'status': 'connection_error',
                        'message': f'Connection error after {max_retries + 1} attempts: {str(e)}',
                        'response_data': None
                    }
            
            except requests.exceptions.Timeout as e:
                logger.error(f"❌ Timeout error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                if attempt < max_retries:
                    logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    return {
                        'success': False,
                        'resource_id': None,
                        'status': 'timeout_error',
                        'message': f'Timeout error after {max_retries + 1} attempts: {str(e)}',
                        'response_data': None
                    }
            
            except Exception as e:
                logger.error(f"❌ Unexpected error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                if attempt < max_retries:
                    logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    return {
                        'success': False,
                        'resource_id': None,
                        'status': 'unexpected_error',
                        'message': f'Unexpected error after {max_retries + 1} attempts: {str(e)}',
                        'response_data': None
                    }
        
        # This should never be reached, but just in case
        return {
            'success': False,
            'resource_id': None,
            'status': 'max_retries_exceeded',
            'message': f'Max retries ({max_retries}) exceeded',
            'response_data': None
        }
    
    def _validate_bundle(self, bundle: Dict) -> bool:
        """
        Validate basic bundle structure
        
        Args:
            bundle: Bundle to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Check required fields
            if not isinstance(bundle, dict):
                logger.error("Bundle must be a dictionary")
                return False
            
            if bundle.get('resourceType') != 'Bundle':
                logger.error("Bundle must have resourceType 'Bundle'")
                return False
            
            if 'type' not in bundle:
                logger.error("Bundle must have a 'type' field")
                return False
            
            if 'entry' not in bundle:
                logger.error("Bundle must have an 'entry' field")
                return False
            
            if not isinstance(bundle['entry'], list):
                logger.error("Bundle entry must be a list")
                return False
            
            # Check each entry has a resource
            for i, entry in enumerate(bundle['entry']):
                if not isinstance(entry, dict):
                    logger.error(f"Entry {i} must be a dictionary")
                    return False
                
                if 'resource' not in entry:
                    logger.error(f"Entry {i} must have a 'resource' field")
                    return False
                
                resource = entry['resource']
                if not isinstance(resource, dict):
                    logger.error(f"Entry {i} resource must be a dictionary")
                    return False
                
                if 'resourceType' not in resource:
                    logger.error(f"Entry {i} resource must have a 'resourceType' field")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating bundle: {e}")
            return False
    
    def get_stored_bundles(self, limit: int = 5) -> Dict:
        """
        Retrieve stored bundles from the server
        
        Args:
            limit: Maximum number of bundles to retrieve
            
        Returns:
            Dict containing bundles and metadata
        """
        try:
            url = f"{self.base_url}/Bundle?_count={limit}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                results = response.json()
                bundles = results.get('entry', [])
                
                logger.info(f"✅ Retrieved {len(bundles)} bundles from server")
                
                return {
                    'success': True,
                    'bundles': bundles,
                    'total': results.get('total', 0),
                    'response_data': results
                }
            elif response.status_code == 404:
                logger.warning("⚠️  No bundles found on server")
                return {
                    'success': True,
                    'bundles': [],
                    'total': 0,
                    'response_data': {'message': 'No bundles found'}
                }
            else:
                logger.error(f"❌ Failed to retrieve bundles: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return {
                    'success': False,
                    'bundles': [],
                    'total': 0,
                    'response_data': {'error': response.text, 'status_code': response.status_code}
                }
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Connection error retrieving bundles: {e}")
            return {
                'success': False,
                'bundles': [],
                'total': 0,
                'response_data': {'error': f'Connection error: {str(e)}'}
            }
        except requests.exceptions.Timeout as e:
            logger.error(f"❌ Timeout error retrieving bundles: {e}")
            return {
                'success': False,
                'bundles': [],
                'total': 0,
                'response_data': {'error': f'Timeout error: {str(e)}'}
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error retrieving bundles: {e}")
            return {
                'success': False,
                'bundles': [],
                'total': 0,
                'response_data': {'error': f'Unexpected error: {str(e)}'}
            }
    
    def get_bundle_by_id(self, bundle_id: str) -> Dict:
        """
        Retrieve a specific bundle by ID
        
        Args:
            bundle_id: ID of the bundle to retrieve
            
        Returns:
            Dict containing the bundle or error information
        """
        try:
            url = f"{self.base_url}/Bundle/{bundle_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                bundle = response.json()
                logger.info(f"✅ Retrieved bundle {bundle_id}")
                
                return {
                    'success': True,
                    'bundle': bundle,
                    'response_data': bundle
                }
            elif response.status_code == 404:
                logger.warning(f"⚠️  Bundle {bundle_id} not found")
                return {
                    'success': False,
                    'bundle': None,
                    'response_data': {'error': 'Bundle not found', 'status_code': 404}
                }
            else:
                logger.error(f"❌ Failed to retrieve bundle {bundle_id}: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return {
                    'success': False,
                    'bundle': None,
                    'response_data': {'error': response.text, 'status_code': response.status_code}
                }
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Connection error retrieving bundle {bundle_id}: {e}")
            return {
                'success': False,
                'bundle': None,
                'response_data': {'error': f'Connection error: {str(e)}'}
            }
        except requests.exceptions.Timeout as e:
            logger.error(f"❌ Timeout error retrieving bundle {bundle_id}: {e}")
            return {
                'success': False,
                'bundle': None,
                'response_data': {'error': f'Timeout error: {str(e)}'}
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error retrieving bundle {bundle_id}: {e}")
            return {
                'success': False,
                'bundle': None,
                'response_data': {'error': f'Unexpected error: {str(e)}'}
            }
    
    def query_resources(self, resource_type: str, params: Dict = None) -> Dict:
        """
        Query resources by type and parameters
        
        Args:
            resource_type: Type of resource to query (e.g., 'Patient', 'Condition', 'Observation')
            params: Dictionary of search parameters (e.g., {'name': 'John', 'gender': 'male'})
            
        Returns:
            Dict containing:
                - success: bool
                - resources: list of matching resources
                - total: total count of matching resources
                - response_data: full server response
        """
        try:
            # Build query URL
            url = f"{self.base_url}/{resource_type}"
            
            # Add query parameters if provided
            if params:
                query_params = []
                for key, value in params.items():
                    if isinstance(value, (list, tuple)):
                        # Handle multiple values for same parameter
                        for v in value:
                            query_params.append(f"{key}={v}")
                    else:
                        query_params.append(f"{key}={value}")
                
                if query_params:
                    url += "?" + "&".join(query_params)
            
            logger.info(f"Querying {resource_type} with URL: {url}")
            response = self.session.get(url)
            
            if response.status_code == 200:
                results = response.json()
                resources = results.get('entry', [])
                
                # Extract actual resources from entries
                resource_list = []
                for entry in resources:
                    if 'resource' in entry:
                        resource_list.append(entry['resource'])
                
                logger.info(f"✅ Found {len(resource_list)} {resource_type} resources")
                
                return {
                    'success': True,
                    'resources': resource_list,
                    'total': results.get('total', len(resource_list)),
                    'response_data': results
                }
            elif response.status_code == 404:
                logger.warning(f"⚠️  No {resource_type} resources found")
                return {
                    'success': True,
                    'resources': [],
                    'total': 0,
                    'response_data': {'message': f'No {resource_type} resources found'}
                }
            else:
                logger.error(f"❌ Failed to query {resource_type}: {response.status_code}")
                logger.error(f"Response: {response.text}")
                
                return {
                    'success': False,
                    'resources': [],
                    'total': 0,
                    'response_data': {'error': response.text, 'status_code': response.status_code}
                }
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Connection error querying {resource_type}: {e}")
            return {
                'success': False,
                'resources': [],
                'total': 0,
                'response_data': {'error': f'Connection error: {str(e)}'}
            }
        except requests.exceptions.Timeout as e:
            logger.error(f"❌ Timeout error querying {resource_type}: {e}")
            return {
                'success': False,
                'resources': [],
                'total': 0,
                'response_data': {'error': f'Timeout error: {str(e)}'}
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error querying {resource_type}: {e}")
            return {
                'success': False,
                'resources': [],
                'total': 0,
                'response_data': {'error': f'Unexpected error: {str(e)}'}
            }
    

    
    def search_patients_by_name(self, name: str) -> Dict:
        """
        Convenience method to search patients by name
        
        Args:
            name: Patient name to search for
            
        Returns:
            Dict containing matching patients
        """
        return self.query_resources("Patient", {"name": name})
    
    def search_conditions_by_code(self, code: str) -> Dict:
        """
        Convenience method to search conditions by code
        
        Args:
            code: Condition code to search for
            
        Returns:
            Dict containing matching conditions
        """
        return self.query_resources("Condition", {"code": code})
    
    def search_observations_by_code(self, code: str) -> Dict:
        """
        Convenience method to search observations by code
        
        Args:
            code: Observation code to search for
            
        Returns:
            Dict containing matching observations
        """
        return self.query_resources("Observation", {"code": code})

def create_sample_bundle() -> Dict:
    """
    Create a sample FHIR bundle with a Patient and Condition for testing
    
    Returns:
        Dict: Sample FHIR bundle
    """
    sample_bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "name": [
                        {
                            "use": "official",
                            "text": "John Doe"
                        }
                    ],
                    "gender": "male",
                    "birthDate": "1980-01-01"
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "subject": {
                        "reference": "Patient/example"
                    },
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "44054006",
                                "display": "Diabetes mellitus"
                            }
                        ],
                        "text": "Diabetes mellitus"
                    },
                    "clinicalStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                                "code": "active",
                                "display": "Active"
                            }
                        ]
                    }
                }
            }
        ]
    }
    
    return sample_bundle

def test_fhir_storage():
    """Test the FHIR storage functionality"""
    print("=== Testing FHIR Storage Module ===")
    
    # Initialize storage
    storage = FHIRStorage()
    
    # Test 1: Create and store sample bundle
    print("\n1. Testing store_bundle with sample bundle:")
    sample_bundle = create_sample_bundle()
    
    result = storage.store_bundle(sample_bundle)
    if result['success']:
        print(f"✅ {result['message']}")
        bundle_id = result['resource_id']
        
        # Test 2: Retrieve the stored bundle
        print(f"\n2. Testing get_bundle_by_id for bundle {bundle_id}:")
        bundle_result = storage.get_bundle_by_id(bundle_id)
        if bundle_result['success']:
            print(f"✅ Successfully retrieved bundle {bundle_id}")
            bundle = bundle_result['bundle']
            entry_count = len(bundle.get('entry', []))
            print(f"   Bundle contains {entry_count} resources")
        else:
            print(f"❌ Failed to retrieve bundle: {bundle_result['response_data']}")
    else:
        print(f"❌ Failed to store bundle: {result['message']}")
    
    # Test 3: Get all stored bundles
    print("\n3. Testing get_stored_bundles:")
    bundles_result = storage.get_stored_bundles(limit=5)
    if bundles_result['success']:
        bundles = bundles_result['bundles']
        print(f"✅ Retrieved {len(bundles)} bundles from server")
        print(f"   Total bundles on server: {bundles_result['total']}")
        
        for i, bundle_entry in enumerate(bundles[:3]):
            bundle = bundle_entry.get('resource', {})
            bundle_id = bundle.get('id', 'Unknown')
            entry_count = len(bundle.get('entry', []))
            print(f"   Bundle {i+1}: ID={bundle_id}, Resources={entry_count}")
    else:
        print(f"❌ Failed to retrieve bundles: {bundles_result['response_data']}")
    
    # Test 4: Query functionality
    print("\n4. Testing query_resources functionality:")
    
    # Test 4a: Query all patients
    print("\n4a. Querying all patients:")
    patients_result = storage.query_resources("Patient")
    if patients_result['success']:
        patients = patients_result['resources']
        print(f"✅ Found {len(patients)} patients on server")
        for i, patient in enumerate(patients[:3]):
            patient_id = patient.get('id', 'Unknown')
            name = "Unknown"
            if 'name' in patient and patient['name']:
                name = patient['name'][0].get('text', 'Unknown')
            print(f"   Patient {i+1}: ID={patient_id}, Name={name}")
    else:
        print(f"❌ Failed to query patients: {patients_result['response_data']}")
    
    # Test 4b: Query patients by name
    print("\n4b. Querying patients by name 'John':")
    john_patients = storage.search_patients_by_name("John")
    if john_patients['success']:
        patients = john_patients['resources']
        print(f"✅ Found {len(patients)} patients named 'John'")
        for i, patient in enumerate(patients[:3]):
            patient_id = patient.get('id', 'Unknown')
            name = "Unknown"
            if 'name' in patient and patient['name']:
                name = patient['name'][0].get('text', 'Unknown')
            print(f"   Patient {i+1}: ID={patient_id}, Name={name}")
    else:
        print(f"❌ Failed to query patients by name: {john_patients['response_data']}")
    
    # Test 4c: Query conditions
    print("\n4c. Querying all conditions:")
    conditions_result = storage.query_resources("Condition")
    if conditions_result['success']:
        conditions = conditions_result['resources']
        print(f"✅ Found {len(conditions)} conditions on server")
        for i, condition in enumerate(conditions[:3]):
            condition_id = condition.get('id', 'Unknown')
            code_text = "Unknown"
            if 'code' in condition and 'text' in condition['code']:
                code_text = condition['code']['text']
            print(f"   Condition {i+1}: ID={condition_id}, Code={code_text}")
    else:
        print(f"❌ Failed to query conditions: {conditions_result['response_data']}")
    
    # Test 4d: Query with multiple parameters
    print("\n4d. Querying patients with multiple parameters:")
    multi_params = {"gender": "male", "_count": "5"}
    multi_result = storage.query_resources("Patient", multi_params)
    if multi_result['success']:
        patients = multi_result['resources']
        print(f"✅ Found {len(patients)} male patients (limited to 5)")
        for i, patient in enumerate(patients):
            patient_id = patient.get('id', 'Unknown')
            gender = patient.get('gender', 'Unknown')
            name = "Unknown"
            if 'name' in patient and patient['name']:
                name = patient['name'][0].get('text', 'Unknown')
            print(f"   Patient {i+1}: ID={patient_id}, Name={name}, Gender={gender}")
    else:
        print(f"❌ Failed to query with multiple parameters: {multi_result['response_data']}")
    
    print("\n=== FHIR Storage Test Complete ===")

def test_error_handling():
    """Test error handling with invalid bundles"""
    print("\n=== Testing Error Handling ===")
    
    storage = FHIRStorage()
    
    # Test 1: Invalid bundle structure
    print("\n1. Testing invalid bundle structure:")
    invalid_bundle = {
        "resourceType": "Bundle",
        "type": "collection"
        # Missing 'entry' field
    }
    
    result = storage.store_bundle(invalid_bundle)
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Success: {result['success']}")
    
    # Test 2: Bundle with invalid resource
    print("\n2. Testing bundle with invalid resource:")
    invalid_resource_bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "InvalidResource",
                    "id": "invalid-1"
                }
            }
        ]
    }
    
    result = storage.store_bundle(invalid_resource_bundle)
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Success: {result['success']}")
    
    # Test 3: Empty bundle
    print("\n3. Testing empty bundle:")
    empty_bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": []
    }
    
    result = storage.store_bundle(empty_bundle)
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Success: {result['success']}")
    
    # Test 4: Malformed JSON (not a dict)
    print("\n4. Testing malformed bundle (not a dict):")
    result = storage.store_bundle("not a bundle")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Success: {result['success']}")
    
    print("\n=== Error Handling Test Complete ===")

def main():
    """Main function to run FHIR storage tests"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            test_fhir_storage()
        elif command == "store":
            # Store a sample bundle
            storage = FHIRStorage()
            sample_bundle = create_sample_bundle()
            result = storage.store_bundle(sample_bundle)
            print(json.dumps(result, indent=2))
        elif command == "list":
            # List stored bundles
            storage = FHIRStorage()
            result = storage.get_stored_bundles(limit=10)
            print(json.dumps(result, indent=2))
        elif command == "query":
            # Query resources
            storage = FHIRStorage()
            if len(sys.argv) > 3:
                resource_type = sys.argv[2]
                name = sys.argv[3]
                if resource_type.lower() == "patient":
                    result = storage.search_patients_by_name(name)
                else:
                    result = storage.query_resources(resource_type, {"name": name})
                print(json.dumps(result, indent=2))
            else:
                print("Usage: python fhir_storage.py query <resource_type> <name>")
                print("Example: python fhir_storage.py query Patient John")
        elif command == "error":
            # Test error handling
            test_error_handling()
        else:
            print("Usage: python fhir_storage.py [test|store|list|query|error]")
    else:
        # Run default test
        test_fhir_storage()

if __name__ == "__main__":
    main()
