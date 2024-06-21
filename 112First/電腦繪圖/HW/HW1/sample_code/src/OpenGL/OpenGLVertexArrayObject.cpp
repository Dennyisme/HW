#include "OpenGLVertexArrayObject.hpp"

#include "OpenGLException.hpp"

#include "Utils/Global.hpp"

#include <iostream>


namespace OpenGL
{

namespace Detail
{

constexpr GLuint noId{0};

bool isCreated(GLuint id) noexcept;

inline bool isCreated(GLuint id) noexcept { return static_cast<bool>(id); }

} // namespace Detail

OpenGLVertexArrayObject::OpenGLVertexArrayObject() : id_{Detail::noId}
{
    std::cout << "5OpenGLVertexArrayObject"
              << "\n";

    create();
}

OpenGLVertexArrayObject::OpenGLVertexArrayObject(
    OpenGLVertexArrayObject &&other) noexcept
    : id_{std::move(other.id_)}
{
    std::cout << "555OpenGLVertexArrayObject"
              << "\n";

    other.id_ = 0; // Avoid double deletion
}

OpenGLVertexArrayObject &
OpenGLVertexArrayObject::operator=(OpenGLVertexArrayObject &&other) noexcept
{
    std::cout << "5operator"
              << "\n";

    if (this != &other)
    {
        if (Detail::isCreated(id_))
        {
            tidy();
        }

        id_ = std::move(other.id_);

        other.id_ = Detail::noId; // Avoid double deletion
    }

    return *this;
}

OpenGLVertexArrayObject::~OpenGLVertexArrayObject()
{
    std::cout << "5~OpenGLVertexArrayObject"
              << "\n";

    if (Detail::isCreated(id_))
    {
        tidy();
    }
}

void OpenGLVertexArrayObject::bind() noexcept
{

    PROGRAM_ASSERT(Detail::isCreated(id_));

    // Fill in the Blank
    glBindVertexArray(id_);
}

GLuint OpenGLVertexArrayObject::id() const noexcept { return id_; }

void OpenGLVertexArrayObject::release() noexcept
{

    PROGRAM_ASSERT(Detail::isCreated(id_));

    // Fill in the Blank
    glBindVertexArray(0);
}

void OpenGLVertexArrayObject::create()
{
    std::cout << "5create"
              << "\n";

    PROGRAM_ASSERT(!Detail::isCreated(id_));

    // Fill in the Blank
    glGenVertexArrays(1, &id_);

    if (!Detail::isCreated(id_))
    {
        throw OpenGLException("OpenGLVertexArrayObject failed to instantiate.");
    }
}

void OpenGLVertexArrayObject::tidy() noexcept
{
    std::cout << "5tidy"
              << "\n";

    PROGRAM_ASSERT(Detail::isCreated(id_));

    // Fill in the Blank
    glDeleteVertexArrays(1, &id_);

    id_ = Detail::noId;
}

} // namespace OpenGL
