#ifndef SCENE_NODE_H
#define SCENE_H
#include <vector>
#include "model.h"
#include "shader.h"
#include "../lib/glm/glm.hpp"

class Scene {
public:
    glm::mat4 transformation;
    Model* model;
    std::vector<Scene*> children;

    Scene(Model* model);
    ~Scene();
    
    
    void draw(Shader& shader, const glm::mat4& parentTransform = glm::mat4(1.0));
    void setTransfer(const glm::mat4& matrix);
    void addChild(Scene* child);
    const glm::mat4& getTransfor() const;
};

#endif
