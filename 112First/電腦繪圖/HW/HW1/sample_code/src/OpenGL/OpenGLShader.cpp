#include "OpenGLShader.hpp"

#include "OpenGLException.hpp"

#include "Utils/FileIO/FileIn.hpp"
#include "Utils/Global.hpp"

#include <cstring>

#include <string>
#include <iostream>


namespace OpenGL
{

namespace Detail
{

constexpr GLuint noId{0};

bool compileStatus(GLuint id) noexcept;
bool isCreated(GLuint id) noexcept;

inline bool compileStatus(GLuint id) noexcept
{
    GLint status;
    // Fill in the Blank
    glGetShaderiv(id, GL_COMPILE_STATUS, &status);
    std::cout << "2compileStatus"
              << "\n";

    return (status == GL_TRUE);
}

inline bool isCreated(GLuint id) noexcept { return static_cast<bool>(id); }

} // namespace Detail

OpenGLShader::OpenGLShader(OpenGLShader::Type type)
    : id_{Detail::noId}, type_{type}
{
    std::cout << "22OpenGLShader"
              << "\n";

    create();
}

OpenGLShader::OpenGLShader(OpenGLShader &&other) noexcept
    : id_{std::move(other.id_)}, type_{std::move(other.type_)}
{
    other.id_ = Detail::noId; // Avoid double deletion
    std::cout << "2OpenGLShader"
              << "\n";
}

OpenGLShader &OpenGLShader::operator=(OpenGLShader &&other) noexcept
{
    std::cout << "222222"
              << "\n";

    if (this != &other)
    {
        if (Detail::isCreated(id_))
        {
            tidy();
        }

        id_ = std::move(other.id_);
        type_ = std::move(other.type_);

        other.id_ = Detail::noId; // Avoid double deletion
    }

    return *this;
}

OpenGLShader::~OpenGLShader()
{
    std::cout << "2OpenGLShader"
              << "\n";

    if (Detail::isCreated(id_))
    {
        tidy();
    }
}

bool OpenGLShader::compileFromFile(const char *fileName) noexcept
{
    std::cout << "2compileFromFile"
              << "\n";

    std::string source{FileIO::ReadFileFullText(fileName)};

    return compileFromSource(source.c_str());
}

bool OpenGLShader::compileFromSource(const char *source) noexcept
{
    std::cout << "2compileFromSource"
              << "\n";

    PROGRAM_ASSERT(Detail::isCreated(id_));

    // Fill in the Blank
    glShaderSource(id_, 1, &source, NULL);
    // Fill in the Blank
    glCompileShader(id_);

    return Detail::compileStatus(id_);
}

void OpenGLShader::create()
{
    std::cout << "2create"
              << "\n";

    PROGRAM_ASSERT(!Detail::isCreated(id_));

    // Fill in the Blank
    id_ = glCreateShader(type_);
    

    if (!Detail::isCreated(id_))
    {
        throw OpenGLException("OpenGLShader failed to instantiate.");
    }
}

GLuint OpenGLShader::id() const noexcept { return id_; }

void OpenGLShader::tidy() noexcept
{
    std::cout << "2tidy"
              << "\n";

    PROGRAM_ASSERT(Detail::isCreated(id_));

    // Fill in the Blank
    glDeleteShader(id_);

    id_ = Detail::noId;
}

OpenGLShader::Type OpenGLShader::type() const noexcept { return type_; }

} // namespace OpenGL
