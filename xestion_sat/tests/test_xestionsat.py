# 1: imports of python lib
from datetime import datetime

# 2: import of known third party lib

# 3:  imports of odoo
from .test_common import TestCommonData
from odoo.exceptions import ValidationError

# 4:  imports from odoo modules

# 5: local imports

# 6: Import of unknown third party lib


class XestionsatTest(TestCommonData):
    """Model tests of the xestiónSAT module.
    """

    def setUp(self):
        super(XestionsatTest, self).setUp()
        self.Device = self.env['xestionsat.device']
        self.DeviceComponent = self.env['xestionsat.device.component']

    def test_create_device(self):
        """Device model test.
        """
        users_list = [
            self.partner_1_employee_1.id,
        ]

        # Device 1
        self.device_1 = self.Device.sudo(self.test_admin_1).create(
            {
                # Required fields
                'created_by_id': self.test_admin_1.id,
                'owner_id': self.partner_1.id,
                'headquarter_id': self.partner_1_address_2.id,
                'name': 'Equipo 1',
                'state': 'operational',

                # Optional fields
                'user_ids': [(6, 0, users_list)],
                'internal_id': '20-000001',
                'location': 'Sala de reunións grande',
                'description': 'Equipo para presentacións',
                'observation': 'Saídas de video: 2xHDMI, 1xDVI e 1xVGA',
                'date_registration': datetime.now().strftime('%Y-%m-%d'),
                # 'date_cancellation': '',
            }
        )

        # Check that device is created or not
        assert self.device_1, "Device not created"

        # User assignment checks
        # Add device user
        len_user_ids = len(self.device_1['user_ids'])

        self.device_1['user_ids'] = [(4, self.partner_1_employee_2.id)]
        self.assertEqual(
            len(self.device_1['user_ids']),
            len_user_ids + 1,
            msg='\nAdd Device User ERRO: '
            + '\n Device: ' + self.device_1.name
            + '\n len(user_ids): ' + str(len_user_ids)
        )
        # Remove device user
        len_user_ids = len(self.device_1['user_ids'])

        self.device_1['user_ids'] = [(2, self.partner_1_employee_1.id)]
        self.assertEqual(
            len(self.device_1['user_ids']),
            len_user_ids - 1,
            msg='\nRemove Device User ERRO: '
            + '\n Device: ' + self.device_1.name
            + '\n len(user_ids): ' + str(len_user_ids)
        )

        # Components assignment checks
        # Create a Devices Components
        # Device Component 1 (Product)
        self.componet_1 = self.DeviceComponent.create(
            {
                # Required fields
                'template_id': self.product_1.id,
                # Optional fields
                'serial': '1111',
                'observation': 'Unha observación',
                'date_registration': datetime.now().strftime('%Y-%m-%d'),
                # 'date_cancellation': '',
            }
        )

        # Device Component 2 (Product)
        self.componet_2 = self.DeviceComponent.create(
            {
                # Required fields
                'template_id': self.product_2.id,
                # Optional fields
                'serial': '2222',
                'observation': 'Unha observación',
                'date_registration': datetime.now().strftime('%Y-%m-%d'),
                # 'date_cancellation': '',
            }
        )

        # Device Component 3 (Product)
        self.componet_3 = self.DeviceComponent.create(
            {
                # Required fields
                'template_id': self.product_3.id,
                # Optional fields
                'serial': '3333',
                'observation': 'Unha observación',
                'date_registration': datetime.now().strftime('%Y-%m-%d'),
                # 'date_cancellation': '',
            }
        )

        # Device Component 4 (Product)
        self.componet_4 = self.DeviceComponent.create(
            {
                # Required fields
                'template_id': self.product_4.id,
                # Optional fields
                'serial': '4444',
                'observation': 'Unha observación',
                'date_registration': datetime.now().strftime('%Y-%m-%d'),
                # 'date_cancellation': '',
            }
        )

        componets_list = [
            self.componet_1.id,
            self.componet_2.id,
            self.componet_4.id,
        ]

        # Add device component
        self.device_1['devicecomponents_ids'] = [(6, 0, componets_list)]
        len_devicecomponents_ids = len(self.device_1['devicecomponents_ids'])

        self.device_1['devicecomponents_ids'] = [(4, self.componet_3.id)]
        self.assertEqual(
            len(self.device_1['devicecomponents_ids']),
            len_devicecomponents_ids + 1,
            msg='\nAdd Componet ERRO:'
            + '\n Product: ' + self.device_1.name
            + '\n len(len_devicecomponents_ids): '
                + str(len_devicecomponents_ids)
        )
        # Remove device component
        len_devicecomponents_ids = len(self.device_1['devicecomponents_ids'])

        self.device_1['devicecomponents_ids'] = [(2, self.componet_3.id)]
        self.assertEqual(
            len(self.device_1['devicecomponents_ids']),
            len_devicecomponents_ids - 1,
            msg='\nRemove Componet ERRO:'
            + '\n Product: ' + self.device_1.name
            + '\n len(len_devicecomponents_ids): '
                + str(len_devicecomponents_ids)
        )
        len_user_ids = len(self.device_1['devicecomponents_ids'])

        # Check constraints
        # Check Odoo user constraint
        with self.assertRaises(ValidationError):
            self.device_1.created_by_id = self.test_admin_2

        # Check headquarters constraints
        with self.assertRaises(ValidationError):
            self.device_1.headquarter_id = self.partner_2_address_2

        # Check device user constraint
        with self.assertRaises(ValidationError):
            self.device_1['user_ids'] = (4, self.partner_2_employee_2.id)
