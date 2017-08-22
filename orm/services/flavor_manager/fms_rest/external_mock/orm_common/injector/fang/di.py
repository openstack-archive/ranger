from orm.services.flavor_manager.fms_rest.external_mock.orm_common.injector.fang.dependency_register import DependencyRegister
from orm.services.flavor_manager.fms_rest.external_mock.orm_common.injector.fang.resolver import DependencyResolver
from orm.services.flavor_manager.fms_rest.external_mock.orm_common.injector.fang.resource_provider_register import ResourceProviderRegister


class Di:
    def __init__(self, namespace=None):
        self.namespace = namespace
        self.dependencies = DependencyRegister()
        self.providers = ResourceProviderRegister()
        self.resolver = DependencyResolver(
            dependency_register=self.dependencies,
            resource_provider_register=self.providers)

        # For use as a decorator
        self.dependsOn = self.dependencies.register
