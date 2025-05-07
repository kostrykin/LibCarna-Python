cmake_minimum_required( VERSION 3.5 )

############################################
# Run the tests
############################################

set( TEST_FILES
    test_base
    test_data
    test_drr
    test_dvr
    test_egl
    test_helpers
    test_integration
    test_material
    test_mip
    test_presets
    test_spatial
)

configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/testsuite.py
    ${CMAKE_CURRENT_BINARY_DIR}/../testsuite.py COPYONLY )

execute_process(
    COMMAND ${CMAKE_COMMAND} -E copy_directory
    ${CMAKE_CURRENT_SOURCE_DIR}/results
    ${CMAKE_CURRENT_BINARY_DIR}/../test/results )

foreach( TEST_FILE ${TEST_FILES} )
    configure_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/${TEST_FILE}.py
        ${CMAKE_CURRENT_BINARY_DIR}/../${TEST_FILE}.py COPYONLY )

    add_custom_target(
        ${TEST_FILE}
        COMMAND ${PYTHON_EXECUTABLE} -Xfaulthandler -m unittest ${TEST_FILE}
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