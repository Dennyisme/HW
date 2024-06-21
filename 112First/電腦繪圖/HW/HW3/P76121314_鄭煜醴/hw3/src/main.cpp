#include "../lib/glad/glad.h"
#include <GLFW/glfw3.h>

#include "../lib/glm/glm.hpp"
#include "../lib/glm/gtc/matrix_transform.hpp"
#include "../lib/glm/gtc/type_ptr.hpp"

#include "../include/shader.h"
#include "../include/camera.h"

#include "../include/model.h"
#include "../include/Scene.h"



#include <iostream>

// Globals
bool animation = false;

glm::mat4 legsBaseTransforms[4][2];

// Timing
float lastFrame = 0.0f;
float frameToggled = 0.0f;
float timeSinceLastToggle = 1.0f;

// Some settings
const unsigned int SCR_WIDTH = 1080;
const unsigned int SCR_HEIGHT = 720;

// Camera
Camera camera(glm::vec3(0.0f, 0.0f, 30.0f));
float cameraOrbitRadius = 30.0f;
float rotateAngle = 1.0f;

void framebufferSizeCallback(GLFWwindow* window, int width, int height);
void mouseInput(GLFWwindow * window, double xpos, double ypos);
void scrollInput(GLFWwindow * window, double xoffset, double yoffset);
void keyboardInput(GLFWwindow * window, float deltaTime);

void framebufferSizeCallback(GLFWwindow* window, int width, int height)
{
    // make sure the viewport matches the new window dimensions; note that width and 
    // height will be significantly larger than specified on retina displays.
    glViewport(0, 0, width, height);
}

// Handles user keyboard input. Supposed to be used every frame, so deltaTime can be calculated appropriately.
void keyboardInput(GLFWwindow * window, float deltaTime)
{

    // Exit
    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS)
        glfwSetWindowShouldClose(window, true);

    // Upwards Rotation
    if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS)
        camera.Orbit(UP, cameraOrbitRadius, rotateAngle);

    // Downwards Rotation
    if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS)
        camera.Orbit(DOWN, cameraOrbitRadius, rotateAngle);

    // Rightwards Rotation
    if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS)
        camera.Orbit(RIGHT, cameraOrbitRadius, rotateAngle);

    // Leftwards Rotation
    if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS)
        camera.Orbit(LEFT, cameraOrbitRadius, rotateAngle);


    // Pause / Start
    if (glfwGetKey(window, GLFW_KEY_ENTER) == GLFW_PRESS)
    {
        if (timeSinceLastToggle > 0.2)
        {
            if (animation == 1)
                animation = 0;
            else
                animation = 1;
            timeSinceLastToggle = 0.0f;
        }
        
    }
        
}


void legRotation(Scene* node, glm::mat4 baseTransform, float beginAgle, float endAngle, float t) {
    float angle = beginAgle + t * (endAngle - beginAgle);
    glm::mat4 rotationTransform = glm::rotate(glm::mat4(1.0f), glm::radians(angle), glm::vec3(0.0f, 0.0f, 1.0f));
    node->setTransfer(baseTransform * rotationTransform);
}


void Animalwalk(Scene* legNodes[][2], float deltaTime) {
    static float walkCycle = 0.0f;

    float maintain = 1.0f;
    walkCycle = fmod(walkCycle + deltaTime, maintain);
    float t = fmod(walkCycle, maintain) / maintain;

    float legRotations[5] = {25.0f, 15.0f, 0.0f, -15.0f, -25.0f};

    int phase = static_cast<int>(t * 5);
    int nextPhase = (phase + 1) % 5;

    glm::mat4 model(1.0);
    for (int i = 0; i < 4; ++i) {
        float beginAgle = legRotations[phase];
        float endAngle = legRotations[nextPhase];
        if(i == 0 || i == 2){
            beginAgle = legRotations[(phase + 3) % 5];
            endAngle = legRotations[(nextPhase + 3) % 5];
        }
        if(i == 1 || i == 3){
            beginAgle = legRotations[(phase) % 5];
            endAngle = legRotations[(nextPhase) % 5];
        }
        legRotation(legNodes[i][0], legsBaseTransforms[i][0], beginAgle, endAngle, t);
    }
}

// Handles mouse scroll wheel. Supposed to be used as the glfw scroll callback.
void scrollInput(GLFWwindow* window, double xoffset, double yoffset)
{
    camera.Zoom(yoffset);
}


int main()
{
    // Initialize and configure GLFW
    glfwInit();
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    GLFWwindow * window = glfwCreateWindow(SCR_WIDTH, SCR_HEIGHT, "hw3", NULL, NULL);
    if (window == NULL)
    {
        std::cerr << "ERROR: Failed to create GLFW window" << std::endl;
        glfwTerminate();
        return -1;
    }

    glfwMakeContextCurrent(window);

    glfwSetFramebufferSizeCallback(window, framebufferSizeCallback);
    glfwSetScrollCallback(window, scrollInput);

    // Load glad
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress))
    {
        std::cout << "Failed to initialize GLAD" << std::endl;
        return -1;
    }

    glEnable(GL_DEPTH_TEST);

    Shader shader("./src/shadder.vs", "./src/shadder.fs");

    // Load the models
    Model cubeModel("./models/cube.obj");
    glm::mat4 model(1.0);

    // scene graph architecture and multiple basic components
    Scene body(&cubeModel);
    body.setTransfer(glm::scale(model, {2.5f, 2.0f, 2.0f}));
    
    Scene head(&cubeModel);
    head.setTransfer(
        glm::translate(model, {-1.7f, 0.0f, 0.0f}) *
        glm::scale(model, {0.7f, 0.7f, 0.7f})
    );
    body.addChild(&head);

    Scene eye_1(&cubeModel);
    eye_1.setTransfer(
        glm::translate(model, {0.3f, 1.3f, 0.5f}) *
        glm::scale(model, {0.3f, 0.3f, 0.3f})
    );
    head.addChild(&eye_1);

    Scene eye_2(&cubeModel);
    eye_2.setTransfer(
        glm::translate(model, {0.3f, 1.3f, -0.5f}) *
        glm::scale(model, {0.3f, 0.3f, 0.3f})
    );
    head.addChild(&eye_2);

    Scene tail(&cubeModel);
    tail.setTransfer(
        glm::translate(model, {1.3f, 0.3f, 0.0f}) * 
        glm::scale(model, {1.0f, 0.3f, 0.3f}) *
        glm::rotate(model, glm::radians(0.0f), {1, 0, 0})
    );
    body.addChild(&tail);

    Scene* legNodes[4][2];
    for (int i = 0; i < 4; ++i) {
        float legXOffset = (i < 2) ? -1.0f : 1.0f;
        for (int j = 0; j < 2; ++j) {
            glm::mat4 legModel(1.0f);
            legNodes[i][j] = new Scene(&cubeModel);
            if (j == 0){
                if (i == 0){
                    legNodes[i][j]->setTransfer(
                        glm::translate(legModel, {-0.6f, -1.3f, 0.7f}) * 
                        glm::scale(legModel, {0.3f, 0.3f, 0.3f})
                    );
                } else if (i == 1){
                    legNodes[i][j]->setTransfer(
                        glm::translate(legModel, {-0.6f, -1.3f, -0.7f}) * 
                        glm::scale(legModel, {0.3f, 0.3f, 0.3f})
                    );
                } else if (i == 2){
                    legNodes[i][j]->setTransfer(
                        glm::translate(legModel, {0.6f, -1.3f, -0.7f}) * 
                        glm::scale(legModel, {0.3f, 0.3f, 0.3f})
                    );
                } else {
                    legNodes[i][j]->setTransfer(
                        glm::translate(legModel, {0.6f, -1.3f, 0.7f}) * 
                        glm::scale(legModel, {0.3f, 0.3f, 0.3f})
                    );
                }
                body.addChild(legNodes[i][j]); 
            } else {
                if (i == 0){
                    legNodes[i][j]->setTransfer(
                        glm::translate(legModel, {0.0f, -1.6f, 0.0f}) * 
                        glm::rotate(legModel, glm::radians(15.0f), {0, 0, 1})
                    );
                } else if (i == 1){
                    legNodes[i][j]->setTransfer(
                        glm::translate(legModel, {0.0f, -1.6f, 0.0f}) * 
                        glm::rotate(legModel, glm::radians(15.0f), {0, 0, 1})
                    );
                } else if (i == 2){
                    legNodes[i][j]->setTransfer(
                        glm::translate(legModel, {0.0f, -1.6f, 0.0f}) * 
                        glm::rotate(legModel, glm::radians(15.0f), {0, 0, 1})
                    );
                } else {
                    legNodes[i][j]->setTransfer(
                        glm::translate(legModel, {0.0f, -1.6f, 0.0f}) * 
                        glm::rotate(legModel, glm::radians(15.0f), {0, 0, 1})
                    );
                }
                legNodes[i][0]->addChild(legNodes[i][j]);
            }
        }
    }

    for (int i = 0; i < 4; ++i) {
        for (int j = 0; j < 2; ++j) {
            legsBaseTransforms[i][j] = legNodes[i][j]->getTransfor();
        }
    }

    while(!glfwWindowShouldClose(window))
    {
        float currentFrame = glfwGetTime();
        float deltaTime = currentFrame - lastFrame;

        if (animation) {
            Animalwalk(legNodes, deltaTime);
        }
        keyboardInput(window, deltaTime);

        glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        glm::mat4 projection = glm::perspective(glm::radians(camera.zoom), (float)SCR_WIDTH / (float)SCR_HEIGHT, 0.1f, 60.0f);
        glm::mat4 view = camera.GetViewMatrix();
 
        // view / projection
        shader.use();
        shader.setMat4("projection", projection);
        shader.setMat4("view", view);
        body.draw(shader);

        glfwSwapBuffers(window);
        glfwPollEvents();
        lastFrame = currentFrame;
    }

    glfwTerminate();
    return 0;
}
