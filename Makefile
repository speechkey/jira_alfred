##
# Utility makefile to assist in automating
# The Alfred Workflow
##
# Relative directory to store temporary dependencies.
TEMP_FOLDER = "_unpacked"
# Relative directory to store the built workflow template.
BUILD_FOLDER = "_build"
# Relative directory containing files to be copied into the workflow.
STATIC_FOLDER = "static"

# A list of python packages to bundle into the workflow
# as a zip file.
PYTHON_PACKAGES = requests \
				  oauthlib \
				  requests-oauthlib \
				  tlslite \

all: clean deps statics bundle

# Remove temp and build cruft.
clean:
	@rm -rf $(TEMP_FOLDER)
	@rm -rf $(BUILD_FOLDER)
	@rm -f pip_log.txt
	@rm -f jira.pem
	@rm -f jira.pub

# Download nad create a zip file with all of the project
# dependencies included.
deps:
	@echo "Creating folders..."
	@mkdir -p $(TEMP_FOLDER) $(BUILD_FOLDER)
	@echo "Grabbing python dependencies..."
	@pip install -t $(TEMP_FOLDER) $(PYTHON_PACKAGES) &> $(BUILD_FOLDER)/pip_log.txt
	@echo "Removing cached bytecode..."
	@find $(TEMP_FOLDER) -name '*.pyc' -delete
	@cd $(TEMP_FOLDER); zip -r9 ../$(BUILD_FOLDER)/deps.zip * &> /dev/null

# Copy static files into the workflow.
statics:
	@cp -r $(STATIC_FOLDER)/* $(BUILD_FOLDER)

# Create the final .alfredworkflow
bundle:
	@cd $(BUILD_FOLDER); zip -r9 ../$(TEMP_FOLDER)/jira_alfred.alfredworkflow *
	@mv $(TEMP_FOLDER)/jira_alfred.alfredworkflow $(BUILD_FOLDER)

# Create a testing key-pair using OpenSSL
certs:
	openssl genrsa -out jira.pem 1024
	openssl rsa -in jira.pem -pubout -out jira.pub