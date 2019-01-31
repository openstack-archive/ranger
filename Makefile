# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

DOCKER_REGISTRY            ?= quay.io
IMAGE_NAME                 := ranger rangercli
IMAGE_PREFIX               ?= attcomdev
IMAGE_TAG                  ?= ocata
HELM                       ?= helm
LABEL                      ?= commit-id
PROXY                      ?= http://proxy.foo.com:8000
NO_PROXY                   ?= localhost,127.0.0.1,.svc.cluster.local
USE_PROXY                  ?= true
RANGER_USER                := ranger

IMAGE := ${DOCKER_REGISTRY}/${IMAGE_PREFIX}/${IMAGE_NAME}:${IMAGE_TAG}
IMAGE_DIR:=images/$(IMAGE_NAME)

# Build ranger Docker image for this project
.PHONY: images
#Build all images in the list
images: $(IMAGE_NAME)
#sudo make images will build and run ranger and rangercli
 $(IMAGE_NAME):
	@echo
	@echo "===== Processing [$@] image ====="
	@make build_$@ IMAGE=${DOCKER_REGISTRY}/${IMAGE_PREFIX}/$@:${IMAGE_TAG} IMAGE_DIR=images/$@ IMAGE_NAME=$@

# Create tgz of the chart
.PHONY: charts
charts: clean
	$(HELM) dep up charts/ranger
	$(HELM) package charts/ranger

# Perform linting
.PHONY: lint
lint: pep8 helm_lint

# Dry run templating of chart
.PHONY: dry-run
dry-run: clean
	tools/helm_tk.sh $(HELM)

# Make targets intended for use by the primary targets above.
.PHONY: build_ranger
build_ranger:

ifeq ($(USE_PROXY), true)
	docker build --network host -t $(IMAGE) --label $(LABEL) -f $(IMAGE_DIR)/Dockerfile \
                --build-arg user=$(RANGER_USER) \
		--build-arg http_proxy=$(PROXY) \
		--build-arg https_proxy=$(PROXY) \
		--build-arg HTTP_PROXY=$(PROXY) \
		--build-arg HTTPS_PROXY=$(PROXY) \
		--build-arg no_proxy=$(NO_PROXY) \
		--build-arg NO_PROXY=$(NO_PROXY) .
else
	docker build --network host -t $(IMAGE) --label $(LABEL) -f $(IMAGE_DIR)/Dockerfile --build-arg user=$(RANGER_USER) .
endif

.PHONY: build_rangercli
build_rangercli:

ifeq ($(USE_PROXY), true)
	docker build --network host -t $(IMAGE) --label $(LABEL) -f $(IMAGE_DIR)/Dockerfile \
		--build-arg http_proxy=$(PROXY) \
		--build-arg https_proxy=$(PROXY) \
		--build-arg HTTP_PROXY=$(PROXY) \
		--build-arg HTTPS_PROXY=$(PROXY) \
		--build-arg no_proxy=$(NO_PROXY) \
		--build-arg NO_PROXY=$(NO_PROXY) .
else
	docker build --network host -t $(IMAGE) --label $(LABEL) -f $(IMAGE_DIR)/Dockerfile .
endif


.PHONY: clean
clean:
	rm -rf build
	helm delete helm-template ||:

.PHONY: pep8
pep8:
	cd ../../; tox -e pep8

.PHONY: helm_lint
helm_lint: clean
	tools/helm_tk.sh $(HELM)
	$(HELM) lint charts/ranger

