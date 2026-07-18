from posehud import WindowNotFoundError, poses


def main() -> None:
    print("reading VRChat HUD... (Ctrl+C to stop)")
    try:
        for pose in poses():
            print(
                f"t={pose.time_ms}  "
                f"X={pose.position.x:+8.3f}  "
                f"Y={pose.position.y:+8.3f}  "
                f"Z={pose.position.z:+8.3f}  "
                f"roll={pose.roll_deg:+6.2f}  "
                f"pitch={pose.pitch_deg:+6.2f}  "
                f"yaw={pose.yaw_deg:+7.2f}"
            )
    except KeyboardInterrupt:
        pass
    except WindowNotFoundError as exc:
        raise SystemExit(f"error: {exc}")


if __name__ == "__main__":
    main()
