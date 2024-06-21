#include "OpenGLTexture.hpp"

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

OpenGLTexture::OpenGLTexture()
    : id_{Detail::noId}, format_{0}, height_{0}, width_{0}, mipmapCount_{0},
      minificationFilter_{Filter::Nearest},
      magnificationFilter_{Filter::Linear}, wrapOption_{WrapOption::Repeat}
{
    std::cout << "4OpenGLTexture"
              << "\n";
}

OpenGLTexture::OpenGLTexture(GLsizei width, GLsizei height, GLenum format,
                             const std::vector<unsigned char> &buffer,
                             Filter minificationFilter,
                             Filter magnificationFilter, WrapOption wrapOption)
    : id_{0}, format_{format}, height_{height}, width_{width},
      minificationFilter_{minificationFilter},
      magnificationFilter_{magnificationFilter}, wrapOption_{wrapOption}
{
    create();

    bind();

    bindBuffer(buffer);
    std::cout << "444OpenGLTexture"
              << "\n";
}

OpenGLTexture::OpenGLTexture(OpenGLTexture &&other) noexcept
    : id_{std::move(other.id_)}, format_{std::move(other.format_)},
      height_{std::move(other.height_)}, width_{std::move(other.width_)},
      minificationFilter_{std::move(other.minificationFilter_)},
      magnificationFilter_{std::move(other.magnificationFilter_)},
      wrapOption_{std::move(other.wrapOption_)}
{
    std::cout << "44444OpenGLTexture"
              << "\n";
    other.id_ = Detail::noId; // Avoid double deletion
}

OpenGLTexture &OpenGLTexture::operator=(OpenGLTexture &&other) noexcept
{
    if (this != &other)
    {
        if (Detail::isCreated(id_))
        {
            tidy();
        }

        id_ = std::move(other.id_);
        format_ = std::move(other.format_);
        height_ = std::move(other.height_);
        width_ = std::move(other.width_);
        mipmapCount_ = std::move(other.mipmapCount_);
        minificationFilter_ = std::move(other.minificationFilter_);
        magnificationFilter_ = std::move(other.magnificationFilter_);
        wrapOption_ = std::move(other.wrapOption_);

        other.id_ = Detail::noId; // Avoid double deletion
    }
    std::cout << "4operator"
              << "\n";
    ;

    return *this;
}

OpenGLTexture::~OpenGLTexture()
{
    if (Detail::isCreated(id_))
    {
        tidy();
    }
    std::cout << "4~OpenGLTexture"
              << "\n";
    ;
}

void OpenGLTexture::bind()
{
    PROGRAM_ASSERT(Detail::isCreated(id_));

    // Fill in the Blank
    glBindTexture(GL_TEXTURE_2D, id_);
}

void OpenGLTexture::bindBuffer(const std::vector<unsigned char> &buffer) 
{
	// Fill in the Blank
    // (bind)
    glBindBuffer(GL_ARRAY_BUFFER, id_);

	// (parameter setup: filter and warpping method)
    setMinificationFilter(minificationFilter_);
    setMagnificationFilter(magnificationFilter_);
    setWrapOption(wrapOption_);

	// (data specify)
    glTexImage2D(GL_TEXTURE_2D, 0, format_, width_, height_, 0, GL_RGB,
                 GL_UNSIGNED_BYTE, &buffer[0]);
	// (generate mipmap)
    glGenerateMipmap(GL_TEXTURE_2D);
    std::cout << "4bindBuffer"
              << "\n";
    ;
}

void OpenGLTexture::create()
{
    PROGRAM_ASSERT(!Detail::isCreated(id_));

    // Fill in the Blank
    glGenTextures(1, &id_);

    if (!Detail::isCreated(id_))
    {
        throw OpenGLException(
            "OpenGLTexture instantiate failed at 'glGenTextures'.");
    }
    std::cout << "4create"
              << "\n";
    ;
}

GLenum OpenGLTexture::format() const { return format_; }

GLsizei OpenGLTexture::height() const { return height_; }

GLuint OpenGLTexture::id() const { return id_; }

OpenGLTexture::Filter OpenGLTexture::magnificationFilter() const
{
    std::cout << "4magnificationFilter"
              << "\n";
    ;
    return magnificationFilter_;
}

OpenGLTexture::Filter OpenGLTexture::minificationFilter() const
{
    std::cout << "4minificationFilter"
              << "\n";
    return minificationFilter_;
}

void OpenGLTexture::release()
{
    PROGRAM_ASSERT(Detail::isCreated(id_));

    // Fill in the Blank
    glBindTexture(GL_TEXTURE_2D, 0);
}

void OpenGLTexture::setMagnificationFilter(Filter filter)
{
    PROGRAM_ASSERT(Detail::isCreated(id_));
    magnificationFilter_ = filter;

    bind();
    // Fill in the Blank
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, magnificationFilter_);

    release();
    std::cout << "4setMagnificationFilter"
              << "\n";
}

void OpenGLTexture::setMinificationFilter(Filter filter)
{
    PROGRAM_ASSERT(Detail::isCreated(id_));
    minificationFilter_ = filter;

    bind();
    // Fill in the Blank
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, minificationFilter_);

    release();
    std::cout << "4setMinificationFilter"
              << "\n";
}

void OpenGLTexture::setWrapOption(WrapOption option)
{
    PROGRAM_ASSERT(Detail::isCreated(id_));
    wrapOption_ = option;

    bind();
    // Fill in the Blank
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrapOption_);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrapOption_);

    release();
    std::cout << "4setWrapOption"
              << "\n";
}

void OpenGLTexture::tidy()
{
    PROGRAM_ASSERT(Detail::isCreated(id_));

    // Fill in the Blank
    glDeleteTextures(1, &id_);


    id_ = 0;
    std::cout << "4tidy"
              << "\n";
}

GLsizei OpenGLTexture::width() const { return width_; }

OpenGLTexture::WrapOption OpenGLTexture::wrapOption() const
{
    std::cout << "4wrapOption"
              << "\n";
    return wrapOption_;
}

} // namespace OpenGL
