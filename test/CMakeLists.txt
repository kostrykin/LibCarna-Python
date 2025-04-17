cmake_minimum_required( VERSION 3.5 )

############################################
# Run the tests
############################################

set( TEST_FILES
    test_base
    test_egl
    test_py
)

configure_file( ${CMAKE_CURRENT_SOURCE_DIR}/test_tools.py
                ${CMAKE_CURRENT_BINARY_DIR}/../test_tools.py @ONLY)

foreach( TEST_FILE ${TEST_FILES} )
    configure_file( ${CMAKE_CURRENT_SOURCE_DIR}/${TEST_FILE}.py
                    ${CMAKE_CURRENT_BINARY_DIR}/../${TEST_FILE}.py COPYONLY )

    add_custom_target(
        ${TEST_FILE}
        COMMAND ${PYTHON_EXECUTABLE} -Xfaulthandler -c "import ${TEST_FILE}"
        WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/.."
        DEPENDS ${MODULES}
        COMMENT "Running ${TEST_FILE}..."
    )
endforeach( TEST_FILE )

add_custom_target(
    RUN_TESTSUITE
    DEPENDS ${TEST_FILES}
    COMMENT "Running test suite..."
)