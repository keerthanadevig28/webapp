import requests
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class CloudMetadataService:
    """Service to detect cloud platform and retrieve instance metadata"""

    GCP_METADATA_URL = "http://metadata.google.internal/computeMetadata/v1"
    AWS_METADATA_URL = "http://169.254.169.254/latest/meta-data"
    TIMEOUT = 2  

    def __init__(self):
        self.platform = None
        self._detect_platform()

    def _detect_platform(self) -> None:
        """Detect which cloud platform we're running on at startup"""
        try:
            response = requests.get(
                f"{self.GCP_METADATA_URL}/",
                headers={"Metadata-Flavor": "Google"},
                timeout=self.TIMEOUT
            )
            if response.status_code == 200:
                self.platform = "gcp"
                logger.info("Detected GCP platform")
                return
        except (requests.exceptions.RequestException, requests.exceptions.Timeout):
            pass

        try:
            response = requests.get(
                f"{self.AWS_METADATA_URL}/",
                timeout=self.TIMEOUT
            )
            if response.status_code == 200:
                self.platform = "aws"
                logger.info("Detected AWS platform")
                return
        except (requests.exceptions.RequestException, requests.exceptions.Timeout):
            pass

        logger.warning("No supported cloud platform detected")
        self.platform = None

    def is_cloud_platform_detected(self) -> bool:
        """Check if running on a supported cloud platform"""
        return self.platform is not None

    def get_metadata(self) -> Dict:
        """Get instance metadata based on detected platform"""
        if self.platform is None:
            raise RuntimeError("Not running on a supported cloud platform")

        if self.platform == "gcp":
            return self._get_gcp_metadata()
        elif self.platform == "aws":
            return self._get_aws_metadata()

    # ------------------------------------------------------------------ GCP --

    def _get_gcp_metadata(self) -> Dict:
        """Retrieve GCP instance metadata"""
        headers = {"Metadata-Flavor": "Google"}

        try:
            instance_id = self._gcp_get("instance/id", headers)
            zone_full = self._gcp_get("instance/zone", headers)
            machine_type_full = self._gcp_get("instance/machine-type", headers)

            # Extract short form: 'projects/.../zones/us-east1-b' -> 'us-east1-b'
            region = zone_full.split('/')[-1] if zone_full else None

            # Extract short form: 'projects/.../machineTypes/e2-medium' -> 'e2-medium'
            machine_type = machine_type_full.split('/')[-1] if machine_type_full else None

            network_interfaces = self._get_gcp_network_interfaces(headers)

            return {
                "cloud_platform": "gcp",
                "instance_id": instance_id,
                "region": region,
                "machine_type": machine_type,
                "network_interfaces": network_interfaces
            }
        except Exception as e:
            logger.error(f"Error retrieving GCP metadata: {e}")
            raise RuntimeError(f"Failed to retrieve GCP metadata: {e}")

    def _get_gcp_network_interfaces(self, headers: Dict) -> List[Dict]:
        """Get GCP network interface information"""
        interfaces = []
        index = 0

        while True:
            try:
                base_path = f"instance/network-interfaces/{index}"

                private_ip = self._gcp_get(f"{base_path}/ip", headers)
                network_full = self._gcp_get(f"{base_path}/network", headers)
                network = network_full.split('/')[-1] if network_full else None

                try:
                    public_ip = self._gcp_get(
                        f"{base_path}/access-configs/0/external-ip", headers
                    ) or None
                except Exception:
                    public_ip = None

                interfaces.append({
                    "private_ip": private_ip,
                    "public_ip": public_ip,
                    "network": network
                })

                index += 1
            except Exception:
                break

        return interfaces

    def _gcp_get(self, path: str, headers: Dict) -> str:
        """Helper to get GCP metadata"""
        url = f"{self.GCP_METADATA_URL}/{path}"
        response = requests.get(url, headers=headers, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response.text.strip()

    # ------------------------------------------------------------------ AWS --

    def _get_aws_metadata(self) -> Dict:
        """Retrieve AWS instance metadata"""
        try:
            instance_id = self._aws_get("instance-id")
            availability_zone = self._aws_get("placement/availability-zone")
            instance_type = self._aws_get("instance-type")

            network_interfaces = self._get_aws_network_interfaces()

            return {
                "cloud_platform": "aws",
                "instance_id": instance_id,
                "region": availability_zone,
                "machine_type": instance_type,
                "network_interfaces": network_interfaces
            }
        except Exception as e:
            logger.error(f"Error retrieving AWS metadata: {e}")
            raise RuntimeError(f"Failed to retrieve AWS metadata: {e}")

    def _get_aws_network_interfaces(self) -> List[Dict]:
        """Get AWS network interface information"""
        interfaces = []

        try:
            macs_text = self._aws_get("network/interfaces/macs/")
            macs = [mac.strip() for mac in macs_text.split('\n') if mac.strip()]

            for mac in macs:
                mac_base = f"network/interfaces/macs/{mac}"

                private_ips_text = self._aws_get(f"{mac_base}/local-ipv4s")
                private_ip = private_ips_text.split('\n')[0].strip() or None

                vpc_id = self._aws_get(f"{mac_base}/vpc-id")

                try:
                    public_ips_text = self._aws_get(f"{mac_base}/public-ipv4s")
                    public_ip = public_ips_text.split('\n')[0].strip() or None
                except Exception:
                    public_ip = None

                interfaces.append({
                    "private_ip": private_ip,
                    "public_ip": public_ip,
                    "network": vpc_id
                })

            return interfaces
        except Exception as e:
            logger.error(f"Error retrieving AWS network interfaces: {e}")
            raise RuntimeError(f"Failed to retrieve AWS network interfaces: {e}")

    def _aws_get(self, path: str) -> str:
        """Helper to get AWS metadata"""
        url = f"{self.AWS_METADATA_URL}/{path}"
        response = requests.get(url, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response.text.strip()