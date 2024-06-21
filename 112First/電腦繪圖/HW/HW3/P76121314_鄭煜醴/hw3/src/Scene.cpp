#include "../include/Scene.h"

Scene::Scene(Model* model) : model(model), transformation(glm::mat4(1.0f)) {}

Scene::~Scene() {
    for (Scene* child : children) {
        delete child;
    }
    children.clear();
}

void Scene::setTransfer(const glm::mat4& matrix) {
    transformation = matrix;
}

const glm::mat4& Scene::getTransfor() const {
    return transformation;
}

void Scene::draw(Shader& shader, const glm::mat4& parentTransform) {
    glm::mat4 globalTransformation = parentTransform * transformation;
    if (model) {
        shader.use();
        shader.setMat4("model", globalTransformation);
        model->Draw(shader);
    }
    for (Scene* child : children) {
        child->draw(shader, globalTransformation);
    }
}

void Scene::addChild(Scene* child) {
    children.push_back(child);
}

