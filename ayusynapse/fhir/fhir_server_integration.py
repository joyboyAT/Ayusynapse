#!/usr/bin/env python3
"""
FHIR Server Integration - Connect to HAPI FHIR server for storage and querying
"""

import json
import requests
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class FHIRServerIntegration:
    """Integration with HAPI FHIR server for storage and querying"""
    
    def __init__(self, base_url: str = "http://hapi.fhir.org/baseR4"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json'
        })
        
        # Test connection on initialization
        self.test_connection()
    
    def test_connection(self) -> bool:
        """
        Test connection to FHIR server
        
        Returns:
            bool: True if connection successful, False otherwise
        """
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
    
    def create_resource(self, resource_type: str, resource_data: Dict) -> Optional[Dict]:
        """
        Create a new FHIR resource on the server
        
        Args:
            resource_type: Type of FHIR resource (e.g., 'Patient', 'Condition')
            resource_data: The resource data to create
            
        Returns:
            Dict: Created resource with server-assigned ID, or None if failed
        """
        try:
            url = f"{self.base_url}/{resource_type}"
            response = self.session.post(url, json=resource_data)
            
            if response.status_code in [201, 200]:
                created_resource = response.json()
                resource_id = created_resource.get('id')
                logger.info(f"✅ Created {resource_type} with ID: {resource_id}")
                return created_resource
            else:
                logger.error(f"❌ Failed to create {resource_type}: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating {resource_type}: {e}")
            return None
    
    def get_resource(self, resource_type: str, resource_id: str) -> Optional[Dict]:
        """
        Retrieve a FHIR resource by ID
        
        Args:
            resource_type: Type of FHIR resource
            resource_id: ID of the resource to retrieve
            
        Returns:
            Dict: The resource data, or None if not found
        """
        try:
            url = f"{self.base_url}/{resource_type}/{resource_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                resource = response.json()
                logger.info(f"✅ Retrieved {resource_type}/{resource_id}")
                return resource
            elif response.status_code == 404:
                logger.warning(f"⚠️  {resource_type}/{resource_id} not found")
                return None
            else:
                logger.error(f"❌ Failed to retrieve {resource_type}/{resource_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error retrieving {resource_type}/{resource_id}: {e}")
            return None
    
    def update_resource(self, resource_type: str, resource_id: str, resource_data: Dict) -> Optional[Dict]:
        """
        Update an existing FHIR resource
        
        Args:
            resource_type: Type of FHIR resource
            resource_id: ID of the resource to update
            resource_data: Updated resource data
            
        Returns:
            Dict: Updated resource, or None if failed
        """
        try:
            url = f"{self.base_url}/{resource_type}/{resource_id}"
            response = self.session.put(url, json=resource_data)
            
            if response.status_code in [200, 201]:
                updated_resource = response.json()
                logger.info(f"✅ Updated {resource_type}/{resource_id}")
                return updated_resource
            else:
                logger.error(f"❌ Failed to update {resource_type}/{resource_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error updating {resource_type}/{resource_id}: {e}")
            return None
    
    def delete_resource(self, resource_type: str, resource_id: str) -> bool:
        """
        Delete a FHIR resource
        
        Args:
            resource_type: Type of FHIR resource
            resource_id: ID of the resource to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            url = f"{self.base_url}/{resource_type}/{resource_id}"
            response = self.session.delete(url)
            
            if response.status_code == 204:
                logger.info(f"✅ Deleted {resource_type}/{resource_id}")
                return True
            else:
                logger.error(f"❌ Failed to delete {resource_type}/{resource_id}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting {resource_type}/{resource_id}: {e}")
            return False
    
    def search_resources(self, resource_type: str, search_params: Dict = None) -> Optional[Dict]:
        """
        Search for FHIR resources
        
        Args:
            resource_type: Type of FHIR resource to search
            search_params: Search parameters (e.g., {'name': 'John', 'gender': 'male'})
            
        Returns:
            Dict: Search results bundle, or None if failed
        """
        try:
            url = f"{self.base_url}/{resource_type}"
            
            if search_params:
                params = []
                for key, value in search_params.items():
                    params.append(f"{key}={value}")
                url += "?" + "&".join(params)
            
            response = self.session.get(url)
            
            if response.status_code == 200:
                results = response.json()
                total = results.get('total', 0)
                logger.info(f"✅ Found {total} {resource_type} resources")
                return results
            else:
                logger.error(f"❌ Failed to search {resource_type}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error searching {resource_type}: {e}")
            return None
    
    def upload_bundle(self, bundle_data: Dict) -> Optional[Dict]:
        """
        Upload a FHIR Bundle to the server
        
        Args:
            bundle_data: FHIR Bundle to upload
            
        Returns:
            Dict: Response from server, or None if failed
        """
        try:
            url = f"{self.base_url}"
            response = self.session.post(url, json=bundle_data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"✅ Uploaded bundle with {len(bundle_data.get('entry', []))} resources")
                return result
            else:
                logger.error(f"❌ Failed to upload bundle: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error uploading bundle: {e}")
            return None
    
    def get_server_capabilities(self) -> Optional[Dict]:
        """
        Get server capabilities (Conformance statement)
        
        Returns:
            Dict: Server capabilities, or None if failed
        """
        try:
            response = self.session.get(f"{self.base_url}/metadata")
            
            if response.status_code == 200:
                capabilities = response.json()
                logger.info("✅ Retrieved server capabilities")
                return capabilities
            else:
                logger.error(f"❌ Failed to get capabilities: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting capabilities: {e}")
            return None
    
    def list_existing_patients(self, limit: int = 10) -> List[Dict]:
        """
        List existing patients on the server (for testing)
        
        Args:
            limit: Maximum number of patients to retrieve
            
        Returns:
            List[Dict]: List of patient resources
        """
        try:
            url = f"{self.base_url}/Patient?_count={limit}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                results = response.json()
                patients = results.get('entry', [])
                logger.info(f"✅ Found {len(patients)} existing patients")
                return patients
            else:
                logger.error(f"❌ Failed to list patients: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error listing patients: {e}")
            return []

def test_hapi_fhir_server():
    """Test the HAPI FHIR server integration"""
    print("=== Testing HAPI FHIR Server Integration ===")
    
    # Initialize integration
    fhir_server = FHIRServerIntegration()
    
    # Test 1: Get server capabilities
    print("\n1. Testing server capabilities:")
    capabilities = fhir_server.get_server_capabilities()
    if capabilities:
        print("✅ Server capabilities retrieved successfully")
        version = capabilities.get('fhirVersion', 'Unknown')
        print(f"   FHIR Version: {version}")
    else:
        print("❌ Failed to get server capabilities")
    
    # Test 2: List existing patients
    print("\n2. Testing list existing patients:")
    patients = fhir_server.list_existing_patients(limit=5)
    if patients:
        print(f"✅ Found {len(patients)} existing patients")
        for i, patient_entry in enumerate(patients[:3]):
            patient = patient_entry.get('resource', {})
            patient_id = patient.get('id', 'Unknown')
            names = patient.get('name', [])
            if names:
                name = names[0].get('text', 'Unknown')
            else:
                name = 'Unknown'
            print(f"   Patient {i+1}: {name} (ID: {patient_id})")
    else:
        print("❌ Failed to list patients")
    
    # Test 3: Create a test patient
    print("\n3. Testing create test patient:")
    test_patient = {
        "resourceType": "Patient",
        "name": [
            {
                "use": "official",
                "text": "Test Patient FHIR Integration"
            }
        ],
        "gender": "unknown",
        "birthDate": "1990-01-01"
    }
    
    created_patient = fhir_server.create_resource("Patient", test_patient)
    if created_patient:
        patient_id = created_patient.get('id')
        print(f"✅ Created test patient with ID: {patient_id}")
        
        # Test 4: Retrieve the created patient
        print("\n4. Testing retrieve created patient:")
        retrieved_patient = fhir_server.get_resource("Patient", patient_id)
        if retrieved_patient:
            print(f"✅ Successfully retrieved patient {patient_id}")
        else:
            print("❌ Failed to retrieve created patient")
        
        # Test 5: Search for patients
        print("\n5. Testing search patients:")
        search_results = fhir_server.search_resources("Patient", {"gender": "unknown"})
        if search_results:
            total = search_results.get('total', 0)
            print(f"✅ Search found {total} patients with gender=unknown")
        else:
            print("❌ Search failed")
        
        # Test 6: Delete the test patient
        print("\n6. Testing delete test patient:")
        if fhir_server.delete_resource("Patient", patient_id):
            print(f"✅ Successfully deleted test patient {patient_id}")
        else:
            print(f"❌ Failed to delete test patient {patient_id}")
    else:
        print("❌ Failed to create test patient")
    
    print("\n=== FHIR Server Integration Test Complete ===")

def upload_clinical_trials_bundle():
    """Upload the clinical trials FHIR bundle to the server"""
    print("=== Uploading Clinical Trials Bundle to FHIR Server ===")
    
    try:
        # Load the clinical trials FHIR data
        with open('clinical_trials_fhir.json', 'r', encoding='utf-8') as f:
            fhir_data = json.load(f)
        
        # Initialize FHIR server integration
        fhir_server = FHIRServerIntegration()
        
        # Upload individual trial bundles
        individual_bundles = fhir_data.get('individual_bundles', [])
        if individual_bundles:
            print(f"Uploading {len(individual_bundles)} individual trial bundles...")
            
            uploaded_count = 0
            for i, trial_bundle in enumerate(individual_bundles):
                trial_id = trial_bundle.get('trial_id', f'trial_{i}')
                fhir_bundle = trial_bundle.get('fhir_bundle')
                
                if fhir_bundle:
                    print(f"Uploading trial {i+1}: {trial_id}")
                    
                    # Extract individual resources from the bundle
                    resources = []
                    for entry in fhir_bundle.get('entry', []):
                        if 'resource' in entry:
                            resources.append(entry['resource'])
                    
                    # First, upload Patient resources and track their IDs
                    patient_id_mapping = {}
                    other_resources = []
                    
                    for resource in resources:
                        resource_type = resource.get('resourceType')
                        if resource_type == 'Patient':
                            # Upload Patient first
                            resource_copy = resource.copy()
                            if 'id' in resource_copy:
                                old_id = resource_copy['id']
                                del resource_copy['id']
                                
                                created_patient = fhir_server.create_resource('Patient', resource_copy)
                                if created_patient:
                                    new_id = created_patient.get('id')
                                    patient_id_mapping[old_id] = new_id
                                    print(f"  ✅ Created Patient with ID: {new_id}")
                                else:
                                    print(f"  ❌ Failed to create Patient")
                        else:
                            other_resources.append(resource)
                    
                    # Now upload other resources with updated Patient references
                    for resource in other_resources:
                        resource_type = resource.get('resourceType')
                        if resource_type:
                            try:
                                # Update Patient references
                                resource_copy = resource.copy()
                                if 'id' in resource_copy:
                                    del resource_copy['id']
                                
                                # Update subject reference if it exists
                                if 'subject' in resource_copy and 'reference' in resource_copy['subject']:
                                    old_reference = resource_copy['subject']['reference']
                                    if old_reference.startswith('Patient/'):
                                        old_patient_id = old_reference.split('/')[1]
                                        if old_patient_id in patient_id_mapping:
                                            new_patient_id = patient_id_mapping[old_patient_id]
                                            resource_copy['subject']['reference'] = f'Patient/{new_patient_id}'
                                
                                created_resource = fhir_server.create_resource(resource_type, resource_copy)
                                if created_resource:
                                    print(f"  ✅ Created {resource_type} with ID: {created_resource.get('id')}")
                                else:
                                    print(f"  ❌ Failed to create {resource_type}")
                            except Exception as e:
                                print(f"  ❌ Error creating {resource_type}: {e}")
                    
                    uploaded_count += 1
                    print(f"  ✅ Completed trial {trial_id}")
            
            print(f"\n✅ Successfully uploaded {uploaded_count} trial bundles to FHIR server")
        else:
            print("❌ No individual bundles found in clinical_trials_fhir.json")
            
    except FileNotFoundError:
        print("❌ clinical_trials_fhir.json not found. Please run fhir_converter.py first.")
    except Exception as e:
        print(f"❌ Error uploading bundle: {e}")

def main():
    """Main function to run FHIR server integration"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            test_hapi_fhir_server()
        elif command == "upload":
            upload_clinical_trials_bundle()
        elif command == "capabilities":
            fhir_server = FHIRServerIntegration()
            capabilities = fhir_server.get_server_capabilities()
            if capabilities:
                print(json.dumps(capabilities, indent=2))
        elif command == "patients":
            fhir_server = FHIRServerIntegration()
            patients = fhir_server.list_existing_patients(limit=10)
            for patient_entry in patients:
                patient = patient_entry.get('resource', {})
                print(f"Patient ID: {patient.get('id')}")
                print(f"Name: {patient.get('name', [{}])[0].get('text', 'Unknown')}")
                print(f"Gender: {patient.get('gender', 'Unknown')}")
                print("---")
        else:
            print("Usage: python fhir_server_integration.py [test|upload|capabilities|patients]")
    else:
        # Run default test
        test_hapi_fhir_server()

if __name__ == "__main__":
    main()
