TEMP_DIR = "_tmp"
BUILD_DIR = "_build"
DIST_DIR = "_dist"
STATIC_DIR = "static"

PROJECT = "jira_alfred"
REQUIREMENTS = "requirements.txt"

all: clean mk_dirs pkgs bundle


mk_dirs:
	@mkdir -p \
		$(TEMP_DIR) \
		$(BUILD_DIR) \
		$(DIST_DIR) \
		$(STATIC_DIR)


clean:
	@rm -rf \
		$(TEMP_DIR) \
		$(BUILD_DIR) \
		$(DIST_DIR)


pkgs:
	@echo "Removing build directory..."
	@rm -rf $(BUILD_DIR)
	@echo "Installing packages from $(REQUIREMENTS)..."
	@pip install \
		--ignore-installed \
		--install-option="--no-compile" \
		--install-option="--single-version-externally-managed" \
		--target=$(BUILD_DIR) \
		-r $(REQUIREMENTS) \
		&> $(TEMP_DIR)/pip.log
	@echo "Zipping up packages..."
	@cd $(BUILD_DIR); \
		zip -r9 ../$(DIST_DIR)/deps.zip * \
			&> ../$(TEMP_DIR)/pkg_zip.log


bundle:
	@cp -r $(STATIC_DIR)/* $(DIST_DIR)
	@cd $(DIST_DIR); \
		zip -r9 ../$(PROJECT).alfredworkflow * \
			&> ../$(TEMP_DIR)/bundle_zip.log

certs:
	openssl genrsa -out jira.pem 1024
 	openssl rsa -in jira.pem -pubout -out jira.pub