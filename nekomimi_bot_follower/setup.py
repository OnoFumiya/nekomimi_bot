import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'nekomimi_bot_follower'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'launch', 'include'), glob('launch/include/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='fumiya',
    maintainer_email='fumiyaono.choi@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'pantilt_follower = nekomimi_bot_follower.pantilt_follower:main',
            'velocity_follower = nekomimi_bot_follower.velocity_follower:main',
        ],
    },
)
